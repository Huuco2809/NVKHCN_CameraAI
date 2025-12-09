import { Injectable } from '@angular/core'; 
import {HttpClient, HttpParams, HttpHeaders} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {Observable, of, throwError} from 'rxjs';
import {catchError, map} from 'rxjs/operators';
 

@Injectable({
  providedIn: 'root',
})
export class CrudService {
  constructor(private http: HttpClient) {}

  // getData(): Observable<any> {
  //   return this.http.get('https://laravelcamera.hpcdongnai.vn/api/auth/cc');
  // }







  async ping(url: string): Promise<any> {
    try {
      const response = await fetch(url, { method: 'GET' });
  
      if (response.ok) {
        const data = await response.json(); // Adjust this based on your expected response format
        return data;
      } else {
        return null; // Or handle error case accordingly
      }
    } catch (error) {
      return null; // Or handle error case accordingly
    }
  }
  

  async  login(email: string, password: string): Promise<any> {
    try {
      const payload = { email, password };
      let url = `${environment.apiServerLogin}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(payload),
      });
  
      if (response.ok) {
        const data = await response.json(); 
        return data;
      } else {
        return null; 
      }
    } catch (error) {
      return null; 
    }
  }

  async refresh(accessToken: string): Promise<any> {
    try {
      const payload = {};
      let url = `${environment.apiServerRefresh}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8; application/x-www-form-urlencoded',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload),
      });
  
      if (response.ok) {
        const data = await response.json(); 
        return data;
      } else {
        return null; 
      }
    } catch (error) {
      return null; 
    }
  }


  async create(accessToken: string, data:any): Promise<any> {
    try {
      const payload = data;
      let url = `${environment.apiServerCreate}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(payload),
      });
  
      if (response.ok) {
        const data = await response.json(); 
        return data;
      } else {
        return null; 
      }
    } catch (error) {
      return null; 
    }
  }


  async read(accessToken: string): Promise<any> {
    try {
      const payload = {};
      let url = `${environment.apiServerRead}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(payload),
      });
  
      if (response.ok) {
        const data = await response.json(); 
        return data;
      } else {
        return null; 
      }
    } catch (error) {
      return null; 
    }
  }


  async readConfig(accessToken: string): Promise<any> {
    try {
      const payload = {};
      let url = `${environment.apiServerReadConfig}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(payload),
      });
  
      if (response.ok) {
        const data = await response.json(); 
        return data;
      } else {
        return null; 
      }
    } catch (error) {
      return null; 
    }
  }

 
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.log(`${operation} failed: ${error.message}`);
      return of(result as T);
    };
  }

}



 