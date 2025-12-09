import {Component, OnInit} from '@angular/core';
import {CameraListComponent} from '../../shared/camera-helpers/camera-list.component';

@Component({
  selector: 'app-home-page',
  templateUrl: './camera.component.html',
  imports: [
    CameraListComponent
  ],
  standalone: true
})
export class CameraComponent implements OnInit {

  constructor() {
  }

  ngOnInit(): void {
  }
}
