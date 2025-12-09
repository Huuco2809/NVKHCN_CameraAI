import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { CameraObject } from '../models/camera.object.model';


@Injectable({ providedIn: 'root' })
export class ObjectsService {
  constructor(
    private readonly http: HttpClient
  ) {
  }

  getAll(): Observable<CameraObject[]> {
    return this.http.get<{ data: CameraObject[] }>('/api/v1/objects/objects-in-area')
      .pipe(map(data => data.data));
  }
}
