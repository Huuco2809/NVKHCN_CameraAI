import { Component, Input, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { Camera } from '../../core/models/camera.model';
import { RouterLink } from '@angular/router';
import { NgForOf } from '@angular/common';
import { MaterialModule } from '../modules/material/material.module';
import { ConfirmDialogService } from '../dialog/confirm-dialog/confirm-dialog.service';
import { SelectionDialogService } from '../dialog/selection-dialog/selection-dialog.service';
import { CamerasService } from '../../core/services/cameras.service';
import { Router } from '@angular/router';

// import { map, tap, catchError, retry } from 'rxjs/operators';
import { StreamDataService } from '../../core/services/stream.data.service';

@Component({
  selector: 'app-camera-preview',
  templateUrl: './camera-preview.component.html',
  imports: [
    MaterialModule,
    RouterLink,
    NgForOf
  ],
  standalone: true,
  providers: [
    StreamDataService,
    ConfirmDialogService,
    SelectionDialogService
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class CameraPreviewComponent implements OnInit {
  constructor(
    public stream: StreamDataService,
    private confirmDialogService: ConfirmDialogService,
    private selectionDialogService: SelectionDialogService,
    private camerasService: CamerasService,
    private readonly router: Router,
  ) { }
  public image: any = undefined
  public listSelection: Camera[] = []
  public nullImage = 'https://thumbnailpreview.com/example.png'
  public cameraObj: any = {}
  delteOptions = {
    title: 'Delete',
    message: 'Do you want to delete this showing camera?',
    cancelText: 'CANCEL',
    confirmText: 'DELETE'
  };

  @Input()
  set camera(camera: Camera) {
    Object.assign(this.cameraObj, camera)
    // console.log(this.cameraObj)
  }

  @Input()
  set selections(selections: Camera[]) {
    Object.assign(this.listSelection, selections)
    // console.log('listSelection', this.listSelection)
  }

  ngOnInit() {
  }

  ngAfterViewInit() {
    if (this.cameraObj.socket_url) {
      this.stream.connect(this.cameraObj.socket_url)
      this.stream.socket$.subscribe({
        next: (msg: any) => {
          // console.log('message received: ', msg?.data)
          const reader = new FileReader()
          reader.onload = (e: any) => this.image = e.target.result
          reader.readAsDataURL(new Blob([msg?.data]))
        },
        error: (err: any) => {
          this.image = 'https://thumbnailpreview.com/example.png'
        }
      })
    }
  }

  deleteCameraShowing(camera: Camera): void {
    if (camera.camera_name !== 'unavailable') {
      this.confirmDialogService.open(this.delteOptions);
      this.confirmDialogService.confirmed().subscribe((confirmed: any) => {
        if (confirmed) {
          this.camerasService.update(camera.camera_id, { showing: false }).pipe(
          ).subscribe((success: boolean) => {
            console.log('disable cam', camera.camera_id, success)
            if (success) {
              alert('Updated successfully!')
              window.location.reload()
            }else{
              alert('Update failed!')
            }
          })
        }
      })
    } else {
      alert('Camera not available! Please update it!')
    }
  }

  updateCameraShowing(camera: Camera): void {
    const current_camera_id = camera?.camera_id
    const items = this.listSelection.map((x) => ({'name':x.camera_name, 'value':x.camera_id}))
    console.log('listSelectionId', items)
    this.selectionDialogService.open({
      title: 'Update',
      message: 'Update to new camera',
      placeholder: 'Select camera',
      items: items,
      cancelText: 'CANCEL',
      confirmText: 'CONFIRM'
    });
      this.selectionDialogService.confirmed().subscribe((data: any) => {
        if (data) {
          if (data?.action && data?.value){
            // enable new cam
            this.camerasService.update(data?.value, { showing: true }).pipe(
              ).subscribe((success: boolean) => {
                console.log('enable new cam', data?.value, success)
                if (success) {
                  // disable current cam
                  if (current_camera_id !== 'unavailable'){
                    this.camerasService.update(current_camera_id, { showing: false }).pipe().subscribe((success: boolean) => {
                      console.log('disable current cam', current_camera_id, success)
                      if (success){
                        alert('Updated successfully!')
                        window.location.reload();
                      }else{
                        alert('Update failed!')
                      }
                    })
                  }else{
                    alert('Updated successfully!')
                    window.location.reload();
                  }
                }else{
                  alert('Update failed!')
                }
              })
          }
        }
      })
  }
}
