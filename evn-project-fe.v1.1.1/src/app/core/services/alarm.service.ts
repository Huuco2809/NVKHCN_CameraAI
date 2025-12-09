import { Injectable } from '@angular/core';
import { CameraStatistics } from '../models/camera-statistic.model';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface CameraData {
  cameraName: string;
  personCount: number;
  animalCount: number;
  vehicleCount: number;
  totalInArea: number;
  goIn: boolean[];
  positions: string[];
}

interface DetectionData {
  person: string[];
  vehicle: string[];
  animal: string[];
}


@Injectable({
  providedIn: 'root',
})
export class AlarmService {
  public lastGoInTrue = {};
  public lastSoundAlarm = {};
  public soundAlarmDelay:any;
  public goInTime:any;

  constructor(private http: HttpClient) {}

  async playAudio(url:any){return new Promise(res=>{var audio=new Audio(url); audio.play();audio.onended=res})}
  async alarm(data_1: any,data_2 : any, goInTime:any, soundAlarmDelay:any ) {
    // Data 1: thong ke 3 object person, vehicle, animal theo tung camera_name
    // Data 2: nguoc lai, thong ke cac camera_name theo 3 object person, vehicle, animal
    // Note: code am thanh alarm o day - code tiep o day, lua chon data1/data2 de lam viec deu ok. 
    // Data1 phu hop it doi tuong, data2 phu hop nhieu doi tuong
 
 
    if(data_1){
      console.log(data_1);
      for (let i = 0; i < data_1.length; i++) {
        let cameraName = data_1[i].cameraName;
        if (data_1[i].goIn.some(element => element === true)){
          // GoIn =  True, tuy chinh am thanh GoIn/GoOut, GoLeft/GoRight tai khu vuc nay 
          if (this.lastGoInTrue[cameraName] && Math.floor( Date.now() / 1000) - this.lastGoInTrue[cameraName] >= goInTime) {
            await this.playAudio("https://audio.hpcdongnai.vn/audios/beep.mp3");
            this.lastSoundAlarm[cameraName] = Math.floor( Date.now() / 1000)
          }

          this.lastGoInTrue[cameraName] = Math.floor( Date.now() / 1000);
        }else{
            // co object nhung thuoc tinh GoIn = False, tuy chinh am thanh co object vao phan vung tai khu vuc nay
            // code here
            if (this.lastSoundAlarm[cameraName] && Math.floor( Date.now() / 1000) - this.lastSoundAlarm[cameraName] >= soundAlarmDelay) {
              console.log('co object binh thuong 2');
              await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_sai_so.mp3");
              this.lastSoundAlarm[cameraName] = Math.floor( Date.now() / 1000)
            }
        }
        if (!this.lastSoundAlarm[cameraName]) { this.lastSoundAlarm[cameraName] = Math.floor( Date.now() / 1000)}
      }
      // console.log("lastSoundAlarm",this.lastSoundAlarm);
      // console.log("lastGoInTrue",this.lastGoInTrue);
    }

    

    // if(data_2){
    //   console.log(data_2);
    //   if(data_2.vehicle.length > 0){
    //     await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_sai_so.mp3");
    //     await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_tang_cao_cap_do_1.mp3");
    //   }
    // }
  }
  
 
 
 
  generateAlarmSentences(x:CameraData[], y:DetectionData): string {
      let alarmSentences: string[] = [];
      for (const key in y) {
          const cameras = y[key];
          if (cameras.length > 0) {
              const cameraNames = this.getUniqueCameraNames(cameras);
              const detectionType = key === 'person' ? 'people' : key + 's';
              alarmSentences.push(`I have ${detectionType} in ${cameraNames}.`);
          }
      }
      return alarmSentences.join(' ');
  }

  private getUniqueCameraNames(cameras: string[]): string {
      const uniqueCameraNames = [...new Set(cameras)];
      return uniqueCameraNames.join(' and ');
  }

 


}



 