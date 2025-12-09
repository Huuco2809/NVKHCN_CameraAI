import {Component, Input, OnInit, OnDestroy, CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {CamerasService} from '../../core/services/cameras.service';
import {Camera} from '../../core/models/camera.model';
import {CameraPreviewComponent} from './camera-preview.component';
import {CameraObjectsComponent} from './camera-objects.component';

import {NgClass, NgForOf, NgIf} from '@angular/common';
import {LoadingState} from '../../core/models/loading-state.model';
import {Subject} from 'rxjs';
import {takeUntil} from 'rxjs/operators';
import { StreamDataService } from '../../core/services/stream.data.service';
import { CameraStatistics } from '../../core/models/camera-statistic.model';

interface myObject{
  [key:string]:object;
}

@Component({
  selector: 'app-camera-list',
  styleUrls: ['camera-list.component.css'],
  templateUrl: './camera-list.component.html',
  imports: [
    CameraPreviewComponent,
    NgForOf,
    NgClass,
    NgIf,
    CameraObjectsComponent
  ],
  standalone: true,
  providers: [
    StreamDataService,
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})



export class CameraListComponent implements OnInit, OnDestroy {
  MAX_NUM_OF_CAMERAS = 15
  cameras: Camera[] = [];
  listShowing: Camera[] = [];
  listSelection: Camera[] = [];
  loading = LoadingState.NOT_LOADED;
  LoadingState = LoadingState;
  destroy$ = new Subject<void>();

 
  constructor (
    public stream: StreamDataService,
    private camerasService: CamerasService
  ) {}


  ngOnInit(): void {
    this.runQuery();
  }

  async ngAfterViewInit() {
    await this.delay(5000);
    this.stream.connect("ws://10.130.9.148:8084/ws/objects-in-area-sort")
    this.stream.socket$.subscribe({
      next: (msg: any) => {
        // console.log(msg?.data)
        // // code more here

        // let x = JSON.parse(msg?.data);
        // let values: object[] = Object.values(x.data);
        // let flattenedArray: object[] = [].concat(...values);

        // if (flattenedArray && flattenedArray.length) {
        //   let groupedObjects = this.groupObjectsByCameraName(flattenedArray);
        //   groupedObjects = this.groupClsNameByCamera(groupedObjects);
        //   this.analyzeCameraData(groupedObjects);
        // }

      },
      error: (err: any) => {
        console.log(err);
      }
    })
  
  }

 
  async analyzeCameraData(data: any) {
    let cameraStatisticsMap: Record<string, CameraStatistics> = {};

    for (const cameraName in data) {
      if (data.hasOwnProperty(cameraName)) {
        const categories = data[cameraName];

        let personCount = 0;
        let animalCount = 0;
        let vehicleCount = 0;
        let totalInArea = 0;
        let goIn: boolean[] = [];
        let positions: string[] = [];

        for (const category in categories) {
          if (categories.hasOwnProperty(category)) {
            const objects = categories[category];

            // Increment the count based on the category
            if (category === 'person') {
              personCount += objects.length;
            } else if (category === 'animal') {
              animalCount += objects.length;
            } else if (category === 'vehicle') {
              vehicleCount += objects.length;
            }

            // Accumulate in_area, go_in, and position counts
            for (const obj of objects) {
              totalInArea += obj.in_area ? 1 : 0;
              goIn.push(obj.go_in || false);
              if(obj.go_in){ 
                // await this.playAudio("https://audio.hpcdongnai.vn/audios/beep.mp3");
                // await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_sai_so.mp3");
                // await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_tang_cao_cap_do_1.mp3");
                console.log("-----------------------");
              }
              positions.push(obj.position || 'N/A');
            }
          }
        }

        // Update or add to the map
        cameraStatisticsMap[cameraName] = {
          cameraName,
          personCount,
          animalCount,
          vehicleCount,
          totalInArea,
          goIn,
          positions,
        };
      }
    }

    // Convert the map values to an array
    const res = Object.values(cameraStatisticsMap);
    // Print the accumulated statistics
    // console.log(res);
    if(res && res.length){
      for(let el of res){
        // console.log(el);
        if(el.personCount > 0){
          // await this.playAudio("https://audio.hpcdongnai.vn/audios/beep.mp3");    
          // await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_sai_so.mp3");
          // await this.playAudio("https://audio.hpcdongnai.vn/audios/nhiet_do_bac_o_do_h1_tang_cao_cap_do_1.mp3");
        }
      }
    }
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  async delay(ms: number): Promise<void> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve();
      }, ms);
    });
  }

  async playAudio(url:any){return new Promise(res=>{var audio=new Audio(url); audio.play();audio.onended=res})}

  groupObjectsByCameraName(objects: any[]): any {
    const groupedObjects = {};

    objects.forEach((object) => {
      const cameraName = object.camera_name;

      if (groupedObjects.hasOwnProperty(cameraName)) {
        groupedObjects[cameraName].push(object);
      } else {
        groupedObjects[cameraName] = [object];
      }
    });

    return groupedObjects;
  }


  groupClsNameByCamera(data: any): any {
    const groupedData = {};

    for (const cameraName in data) {
      if (data.hasOwnProperty(cameraName)) {
        const objects = data[cameraName];
        const groupedObjects = {};

        objects.forEach((object: any) => {
          const clsName = object.cls_name;

          if (groupedObjects.hasOwnProperty(clsName)) {
            groupedObjects[clsName].push({
              camera_id: object.camera_id,
              camera_name: object.camera_name,
              thumbnail: object.thumbnail,
              in_area: object.in_area,
              go_in: object.go_in,
              go_out: object.go_out,
              position: object.position
            });
          } else {
            groupedObjects[clsName] = [{
              camera_id: object.camera_id,
              camera_name: object.camera_name,
              thumbnail: object.thumbnail,
              in_area: object.in_area,
              go_in: object.go_in,
              go_out: object.go_out,
              position: object.position
            }];
          }
        });

        groupedData[cameraName] = groupedObjects;
      }
    }

    return groupedData;
  }

  runQuery() {
    this.loading = LoadingState.LOADING;
    this.cameras = [];

    this.camerasService.getAll().pipe(
      takeUntil(this.destroy$)
    ).subscribe(data => {
      this.loading = LoadingState.LOADED;
      this.cameras = data;
      this.listShowing = this.cameras.filter(cam => cam?.showing);
      // Arrange list showing
      this.listShowing = this.listShowing.sort((a, b) => a.camera_name.localeCompare(b.camera_name));
      // console.log(this.listShowing)
      if (this.listShowing.length > this.MAX_NUM_OF_CAMERAS){
        this.listShowing = this.listShowing.slice(0, this.MAX_NUM_OF_CAMERAS)
      } else if (this.listShowing.length < this.MAX_NUM_OF_CAMERAS){
        const amount = this.MAX_NUM_OF_CAMERAS - this.listShowing.length
        for (var i=0; i<amount; i++){
          this.listShowing.push({
            camera_id : 'unavailable',
            camera_name: 'unavailable',
            rtsp: '',
            thumbnail: 'https://thumbnailpreview.com/example.png',
            socket_url: '',
            showing: true,
            have_object: false,
            tracking: false,
            regions: []
          })
        }
      }
      // console.log(this.listShowing.length)
      // create list selections
      this.listSelection = this.cameras.filter(cam => !this.listShowing.includes(cam))
      // console.log('this.listSelection', this.listSelection)
    });
  }
}
