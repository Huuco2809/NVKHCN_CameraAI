import {Injectable} from '@angular/core';
import {HttpEvent, HttpInterceptor, HttpHandler, HttpRequest} from '@angular/common/http';
import {Observable} from 'rxjs';
import {JwtService} from '../services/jwt.service';

@Injectable({providedIn: 'root'})
export class TokenInterceptor implements HttpInterceptor {
  constructor(private readonly jwtService: JwtService) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    var token = this.jwtService.getToken()
    if (token && token.toLocaleLowerCase().indexOf('bearer') !== 0){
      token = `Bearer ${token}`
    }
    const request = req.clone({
      setHeaders: {
        ...(token ? {Authorization: token} : {})
      }
    });
    return next.handle(request);
  }
}
