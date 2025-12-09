import { Injectable } from '@angular/core'
import { ActivatedRouteSnapshot, CanActivate, RouterStateSnapshot, UrlTree } from '@angular/router'
import { Observable } from 'rxjs'
import { Router } from '@angular/router'
import {UserService} from './core/services/user.service'

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  public isAuthenticated = false
  constructor(public userService: UserService, public router: Router) {
  }
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
      this.userService.isAuthenticated.subscribe(
        (isAuthenticated: boolean) => {
          this.isAuthenticated = isAuthenticated
        }
      )

      if (!this.isAuthenticated) {
        void this.router.navigateByUrl('/login')
        return false
      } else {
        return true
      }
  }
}