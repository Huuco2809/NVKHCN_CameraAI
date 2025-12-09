import { Component, Input, OnInit, OnDestroy, CUSTOM_ELEMENTS_SCHEMA, ViewChild, HostListener } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgForOf, AsyncPipe, NgIf } from '@angular/common';
import { Subject, Subscription, Observable, interval, of, timer } from 'rxjs';
import { takeUntil, switchMap, map, tap } from 'rxjs/operators';
import {MatTooltipModule} from '@angular/material/tooltip';
import { CameraObject } from '../../core/models/camera.object.model';
import { CameraStatistics } from '../../core/models/camera-statistic.model';
import { DataService } from '../../core/services/data.service';
import { AlarmService } from '../../core/services/alarm.service';
import { CrudService } from '../../core/services/crud.service';
import { ObjectsService } from '../../core/services/objects.service';
import { SlickCarouselComponent, SlickCarouselModule } from 'ngx-slick-carousel';
import {HttpClient, HttpParams, HttpHeaders} from '@angular/common/http';
import { DatePipe } from '@angular/common';


@Component({
  selector: 'app-camera-objects',
  templateUrl: './camera-objects.component.html',
  imports: [
    MatTooltipModule,
    RouterLink,
    NgForOf,
    SlickCarouselModule,
  ],
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class CameraObjectsComponent implements OnInit {
  @ViewChild("slickModal")
  slickModal: SlickCarouselComponent
  images: CameraObject[] = []
  slideConfig = {
    "slidesToShow": 10,
    "slidesToScroll": 10,
    "dots": true,
    "autoplay": true,
    "autoplaySpeed": 1000
  };
  subscription !: Subscription;
  public currentTime: String;
  public resArr: CameraStatistics[] = [];
  public data: any[];  
  public analysisResult_1: any;
  public analysisResult_2: any;
  public access_token:any;
  public lastActivity = {}; 
  public lastTime = {}; 
  public refeshTokenTime:any;
  public isNewObjectAfterTime:any;  
  public soundAlarmDelay:any;
  public goInTime:any;
  public delayCycle:any;

  public cameraList = {
    camera_00: 'https://audio.hpcdongnai.vn/audios/beep.mp3',
    camera_01: 'https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_sai_so.mp3',
    camera_02: 'https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_tang_cao_cap_do_1.mp3'
  };
  public ObjectList = {
    notice: 'https://audio.hpcdongnai.vn/audios/thong_bao.mp3',
    person: 'https://audio.hpcdongnai.vn/audios/co_nguoi.mp3',
    animal: 'https://audio.hpcdongnai.vn/audios/co_dong_vat.mp3',
    vehicle: 'https://audio.hpcdongnai.vn/audios/co_xe.mp3'
  };

  constructor(private objectsService: ObjectsService,
    private http: HttpClient,
    private dataService: DataService,
    private crudService: CrudService,
    private alarmService: AlarmService) {
  }

  async ngOnInit() {
    await this.login(); // login to laravel server
    // cho nay nen co do while/alert de no check xem readconfig da sucess hay chua?, lam sau
    await this.readConfig();  // read config from server laravel
    // start loop
    this.lastTime['refreshToken']= Math.floor( Date.now() / 1000);
    this.runLoop();
  }

  async ngAfterViewInit() {}

  async runLoop(){
    let numLoop = 100;
    for (var i=0; i<= numLoop; i++){
      if(i==numLoop){i=0;}
      await this.getAllCameraData();
      // console.log(this.images);
      if (this.images && this.images.length) {
        this.currentTime = this.getCurrentTime()
        let groupedObjects = this.dataService.groupObjectsByCameraName(this.images);
        groupedObjects = this.dataService.groupClsNameByCamera(groupedObjects);
        //Note: Data in of analyzeData_1 is groupedObjects; Data in of analyzeData_2 is this.images;
        this.analysisResult_1 = this.dataService.analyzeData_1(groupedObjects); // better for few camera have object detected 
        this.analysisResult_2 = this.dataService.analyzeData_2(this.images); // better for many camera have object detected, the alarm audio will different
        // console.log('data 1',this.analysisResult_1);
        // console.log('data 2',this.analysisResult_2);
      
      
      
        //******CODE MAKE ALARM***********//
        await this.alarmService.alarm(this.analysisResult_1, this.analysisResult_2, this.goInTime, this.soundAlarmDelay);
        // let alarmSentences = this.alarmService.generateAlarmSentences(this.analysisResult_1, this.analysisResult_2);
        // console.log(alarmSentences);

        //******CODE MAKE REPORT***********//
        // Code refresh to laravel to get access_token
        // access_token expire after 60 mins. We can wait until 60 mins to change it or change it frequenly after a period of time.
        
        if (this.lastTime['refreshToken'] && Math.floor( Date.now() / 1000) - this.lastTime['refreshToken'] >= this.refeshTokenTime) {
          await this.crudService.refresh(this.access_token).then((data) => {
            if (data !== null) {
              this.access_token = data.access_token;
              // console.log('refresh token:', this.access_token);
            } else {
              console.log('Server is not reachable or there was an error.');
            }
          });

          this.lastTime['refreshToken'] = Math.floor( Date.now() / 1000);
       } 

        // // Code read data table (use for statistic in the future) from laravel to get access_token
        // await this.crudService.read(this.access_token).then((data) => {
        //   if (data !== null) {  
        //     console.log('read data:', data);
        //   } else {
        //     console.log('Server is not reachable or there was an error.');
        //   }
        // });

        // code send data to make report
        this.checkCondition2SendData(this.analysisResult_1);
        this.analysisResult_1 = [];

      }
      await this.delay(this.delayCycle);  
    }
  }


  checkCondition2SendData(data:any) {
    if (data && Array.isArray(data)) {
      for (let i = 0; i < data.length; i++) {
        let cameraName = data[i].cameraName;
        const timestampInSeconds = Math.floor( Date.now() / 1000);
 
       if (this.lastActivity[cameraName] && timestampInSeconds - this.lastActivity[cameraName] >= this.isNewObjectAfterTime) {
         // filter camera information if condition satisfy from this.analysisResult_1
         let cameraData= this.getCameraByName(this.analysisResult_1, cameraName);
         // console.log(cameraData);
 
         // get currentTime and currentDate
         const now = new Date();
         let currentT= now.toTimeString().split(' ')[0];  
         const datePipe = new DatePipe('en-US');
         let currentD = datePipe.transform(now, 'dd/MM/yyyy');
         // make data for create POST method
         let data = {
           cameraName: cameraData.cameraName,
           personCount: cameraData.personCount,
           animalCount: cameraData.animalCount,
           vehicleCount: cameraData.vehicleCount,
           totalInArea: cameraData.totalInArea,
           created_time: currentT,  
           created_day: currentD  
         };
        //  console.log("data send",data);
         this.insertDataToDatabase(data);
       }
 
       // update lastActivity time array
       this.lastActivity[cameraName] = timestampInSeconds;
      //  console.log("analysisResult_1",this.analysisResult_1);
      //  console.log("cameraName",cameraName);
      //  console.log("lastActivity",this.lastActivity);
     }
    }
  }

  async  insertDataToDatabase(data:any) {
    await this.crudService.create(this.access_token, data).then((result) => {
      if (result !== null) {
        console.log(`Data ${data.cameraName} inserted successfully. Status:`, result);
      } else {
        console.log(`Error inserting data. Server is not reachable or there was an error.`);
      }
    });
  }
 

  getCameraByName(data: any[], cameraName: string): any { return data.find(camera => camera.cameraName === cameraName); }
  async getAllCameraData(){return new Promise((resolve)=>{this.objectsService.getAll().subscribe(data=>{this.images=data;return resolve("")})})}
  async playAudio(url:any){return new Promise(res=>{var audio=new Audio(url); audio.play();audio.onended=res})}
  delay(ms:number):Promise<void>{return new Promise((resolve)=>{setTimeout(()=>{resolve()},ms)})};
  getCurrentTime():string{const now=new Date();const hours=now.getHours().toString().padStart(2,'0');const minutes=now.getMinutes().toString().padStart(2,'0');const seconds=now.getSeconds().toString().padStart(2,'0');return`${hours}:${minutes}:${seconds}`}


  async readConfig(){
    // read config from server laravel
      await this.crudService.readConfig(this.access_token).then((resp) => {
        if (resp !== null) {
          console.log('config', resp.data);
          this.refeshTokenTime = parseInt(resp.data[0].refeshTokenTime);
          this.isNewObjectAfterTime= parseInt(resp.data[0].isNewObjectAfterTime);
          this.goInTime= parseInt(resp.data[0].goInTime);
          this.soundAlarmDelay= parseInt(resp.data[0].soundAlarmDelay);
          this.delayCycle= parseInt(resp.data[0].delayCycle);
          console.log(this.delayCycle);
        } else {
          console.log('Server is not reachable or there was an error.');
        }
      });
  }


  async login(){
      // Code login to laravel to get access_token
      await this.crudService.login('user1@gmail.com', '12345').then((data) => {
        if (data !== null) {
          this.access_token = data.access_token;
          // console.log('access token:', this.access_token);
        } else {
          console.log('Server is not reachable or there was an error.');
        }
      });
  }


}

       // await this.playAudio("https://audio.hpcdongnai.vn/audios/beep.mp3");
      // await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_sai_so.mp3");
      // await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_tang_cao_cap_do_1.mp3");
      
 