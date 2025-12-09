import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { IResponse } from '../models/response.model'
import { Camera } from '../models/camera.model';

interface CamerasData {
  total?: number,
  pages?: number,
  page?: number,
  page_size?: number,
  items: Camera[],
}

@Injectable({ providedIn: 'root' })
export class CamerasService {
  constructor(
    private readonly http: HttpClient
  ) {
  }

  getAll(): Observable<Camera[]> {
    return this.http.get<{ data: CamerasData }>('/api/v1/cameras')
      .pipe(map(data => data.data.items));
  }

  get(camera_id: String): Observable<Camera> {
    return this.http.get<{ data: Camera }>(`/api/v1/cameras/${camera_id}`)
      .pipe(map(data => data.data));
  }

  update(camera_id: String, body: Object): Observable<boolean> {
    return this.http.put<{ success: boolean }>(`/api/v1/cameras/${camera_id}`, body)
      .pipe(map(data => data.success));
  }

  // update(camera: Partial<Camera>): Observable<Camera> {
  //   return this.http.put<{ camera: Camera }>(`/api/v1/cameras/${camera.camera_id}`, { camera: camera })
  //     .pipe(map(data => data.camera));
  // }
}
