import { Component, OnDestroy, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { NgForOf, NgIf } from '@angular/common';

import { CamerasService } from '../../core/services/cameras.service';
import { Camera } from '../../core/models/camera.model';

import 'fabric';
declare const fabric: any;

@Component({
  selector: 'app-configs-page',
  templateUrl: './configs.component.html',
  imports: [
    NgForOf,
    NgIf,
    ReactiveFormsModule
  ],
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ConfigsComponent implements OnInit, OnDestroy {
  objectKeys = Object.keys

  cameras: Camera[] = []
  camera: any
  regions: any = {}

  formControl = new FormControl()
  options: any;
  destroy$ = new Subject<void>()
  enableDrawPolygonBtn: boolean = false

  //// POLYGON
  canvas: any
  isCanvasDrawn: boolean = false
  min = 99
  max = 999999
  polygonMode = true
  pointArray = new Array()
  lineArray = new Array()
  activeLine: any
  activeShape: any = null

  selectedObject: any = undefined
  isSelectedObject: boolean = false

  constructor(
    private readonly router: Router,
    private camerasService: CamerasService
  ) {
  }

  ngOnInit(): void {
    this.getAllCameras()

    this.canvas = new fabric.Canvas('canvasId'); // { fireRightClick: true }
    // this.canvas.viewportTransform = [1, 0, 0, 1, 0, 0];
  }

  ngAfterViewInit(): void {
    // event mouse:down
    this.canvas.on('mouse:down', options => {
      this.selectedObject = this.canvas.getActiveObject()
      if (this.selectedObject) {
        this.isSelectedObject = true
        this.polygonMode = false
      } else if (options.target && this.pointArray.length){
        if(options.target.id == this.pointArray[0].id){
          this.polygonMode = true
          this.generatePolygon(this.pointArray)
        }
      }

      if (this.polygonMode) {
        this.addPoint(options)
      }else{
        if (!this.enableDrawPolygonBtn){
          this.drawPolygon()
        }
      }
    })

    // event mouse:up
    this.canvas.on('mouse:up', options => {

    })

    // event mouse:move
    this.canvas.on('mouse:move', options => {
      if (this.activeLine && this.activeLine.class == "line") {
        var pointer = this.canvas.getPointer(options.e)
        this.activeLine.set({ x2: pointer.x, y2: pointer.y })

        var points = this.activeShape.get("points")
        points[this.pointArray.length] = {
          x: pointer.x,
          y: pointer.y
        }
        this.activeShape.set({
          points: points
        });
        this.canvas.renderAll()
      }
      this.canvas.renderAll()
    })
  }

  // 1. drawPolygon
  drawPolygon(): void {
    this.polygonMode = true
    this.pointArray = new Array()
    this.lineArray = new Array()
    this.activeLine;
  }

  // 2. addPoint
  addPoint(options): void {
    var random = Math.floor(Math.random() * (this.max - this.min + 1)) + this.min
    var id = new Date().getTime() + random
    var circle = new fabric.Circle({
      radius: 5,
      fill: '#ffffff',
      stroke: 'lightgrey',
      strokeWidth: 0.5,
      left: (options.e.layerX / this.canvas.getZoom()),
      top: (options.e.layerY / this.canvas.getZoom()),
      selectable: false,
      hasBorders: false,
      hasControls: false,
      originX: 'center',
      originY: 'center',
      id: id,
      objectCaching: false
    })

    if (this.pointArray.length == 0) {
      circle.set({
        fill: 'red'
      })
    }
    var points = [(options.e.layerX / this.canvas.getZoom()), (options.e.layerY / this.canvas.getZoom()), (options.e.layerX / this.canvas.getZoom()), (options.e.layerY / this.canvas.getZoom())]
    var line = new fabric.Line(points, {
      strokeWidth: 2,
      fill: '#999999',
      stroke: '#999999',
      class: 'line',
      originX: 'center',
      originY: 'center',
      selectable: false,
      hasBorders: false,
      hasControls: false,
      evented: false,
      objectCaching: false
    })

    if (this.activeShape) {
      let pos = this.canvas.getPointer(options.e)
      let points = this.activeShape.get("points")
      points.push({ x: pos.x, y: pos.y })
      let polygon = new fabric.Polygon(points, {
        stroke: 'lightgrey',
        strokeWidth: 3,
        fill: this.random_rgba(),
        opacity: 1,
        selectable: false,
        hasBorders: false,
        hasControls: false,
        evented: false,
        objectCaching: false
      })

      this.canvas.remove(this.activeShape)
      this.canvas.add(polygon)
      this.activeShape = polygon
      this.canvas.renderAll()
    }
    else {
      let polyPoint = [{ x: (options.e.layerX / this.canvas.getZoom()), y: (options.e.layerY / this.canvas.getZoom()) }]
      let polygon = new fabric.Polygon(polyPoint, {
        stroke: 'lightgrey',
        strokeWidth: 3,
        fill: this.random_rgba(),
        opacity: 1,
        selectable: false,
        hasBorders: false,
        hasControls: false,
        evented: false,
        objectCaching: false
      });
      this.activeShape = polygon
      this.canvas.add(polygon)
    }
    this.activeLine = line

    this.pointArray.push(circle)
    this.lineArray.push(line)

    this.canvas.add(line)
    this.canvas.add(circle)
    this.canvas.selection = false
  }

  // 3. generatePolygon
  generatePolygon(pointArray): void {
    var points = new Array()
    for(var i=0; i<pointArray.length; i++){
      points.push({
        x: pointArray[i].left,
        y: pointArray[i].top
      })
      this.canvas.remove(pointArray[i])
    }
    for(var i=0; i<this.lineArray.length; i++){
      this.canvas.remove(this.lineArray[i])
    }

    this.canvas.remove(this.activeShape).remove(this.activeLine)
    var polygon = new fabric.Polygon(points, {
      stroke: 'lightgrey',
      strokeWidth: 3,
      fill: this.random_rgba(),
      opacity: 1,
      hasBorders: false,
      hasControls: false
    })
    this.canvas.add(polygon)
    const polygonKey = this.createPolygonId(points)
    this.regions[polygonKey] = points

    this.activeLine = null
    this.activeShape = null
    this.polygonMode = false
    this.canvas.selection = true
  }

  random_rgba(): string {
    var o = Math.round, r = Math.random, s = 255;
    return 'rgba(' + o(r() * s) + ',' + o(r() * s) + ',' + o(r() * s) + ',' + r().toFixed(1) + ')';
  }

  delete(): void {
    if (this.selectedObject) {
      try{
        const polygonId = this.createPolygonId(this.selectedObject.points)
        delete this.regions[polygonId]
      }catch{}
      this.canvas.remove(this.selectedObject)
      this.canvas.renderAll()
      this.selectedObject = undefined
      this.isSelectedObject = false
    }
    console.log('regions', this.regions)
  }

  updateCanvas(url: string): void {
    this.canvas.clear()
    this.getMetaImage(url, (err, img) => {
      this.canvas.setWidth(img.naturalWidth)
      this.canvas.setHeight(img.naturalHeight)
    });
    var canvas = this.canvas
    fabric.Image.fromURL(url, function (img) {
      canvas?.setBackgroundImage(img)
    });
    // this.isImageDrawn = true;
  }

  createPolygonId(points: any): string {
    let id = ''
    for (var i = 0; i < points.length; i++) {
      if (points[i][0] === undefined) { //obj
        id += `${points[i].x}_${points[i].y};`
      } else {
        id += `${points[i][0]}_${points[i][1]};`
      }
    }
    return id
  }

  reset(): any {
    if (this.camera) {
      // update canvas
      this.updateCanvas(this.camera.thumbnail)

      // reset data
      this.regions = {}
      this.isCanvasDrawn = false
      this.polygonMode = true
      this.pointArray = new Array()
      this.lineArray = new Array()
      this.activeLine = null
      this.activeShape = null
      this.selectedObject = undefined
      this.isSelectedObject = false

      const regions = this.camera.regions.slice(0)
      // console.log('regions', regions)
      for (let i = 0; i < regions.length; i++) {
        const points = regions[i].map((p) => ({ 'x': p[0], 'y': p[1] }))
        const polygonKey = this.createPolygonId(points)
        const polygon = new fabric.Polygon(points, {
          stroke: 'lightgrey',
          strokeWidth: 3,
          fill: this.random_rgba(),
          opacity: 1,
          hasBorders: false,
          hasControls: false,
          // scaleX: 1,
          // scaleY: 1,
          // objectCaching: false,
          // transparentCorners: false,
          // cornerColor: 'blue'
        })
        this.regions[polygonKey] = points
        this.canvas.add(polygon)
      }
      this.isCanvasDrawn = true
      this.canvas.renderAll()
      console.log('init::this.regions::', this.regions)
    } else {
      alert('Please select camera first!')
    }
  }

  update(): any {
    if (this.camera) {
      var regions = []
      for (const key in this.regions) {
        if (this.regions.hasOwnProperty(key)) {
          regions.push(this.convertPolygon(this.regions[key]))
        }
      }
      // console.log('update regions', regions)
      this.camerasService.update(this.camera.camera_id, { regions: regions }).pipe(
      ).subscribe((success: boolean) => {
        console.log('updated regions cam', this.camera.camera_id, regions, success)
        if (success) {
          alert('Updated successfully!')
          window.location.reload()
        } else {
          alert('Update failed!')
        }
      })
    } else {
      alert('Please select camera first!')
    }
  }

  getMetaImage(url, cb): any {
    const img = new Image();
    img.onload = () => cb(null, img);
    img.onerror = (err) => cb(err);
    img.src = url;
  };

  getAllCameras() {
    this.camerasService.getAll().pipe(
      takeUntil(this.destroy$)
    ).subscribe(data => {
      this.cameras = data;
      // sort list cameras option by camera_name
      this.options = this.cameras.sort((a, b) => a.camera_name.localeCompare(b.camera_name));
      this.options = this.cameras.map((x) => ({ 'name': x.camera_name, 'value': x.camera_id }));

    });
  }

  onChange(e: any) {
    const cameraId = e?.target?.value
    console.log('select cam::', cameraId)
    this.camera = this.cameras.find(x => x.camera_id === cameraId)
    this.reset()
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  convertPolygon(points: any): any {
    return points.map(p => [p?.x, p?.y])
  }
}
