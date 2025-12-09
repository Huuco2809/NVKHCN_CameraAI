import { Injectable } from '@angular/core'
import { Observable, BehaviorSubject } from 'rxjs'

import { JwtService } from './jwt.service'
import { map, distinctUntilChanged, tap, shareReplay } from 'rxjs/operators'
import { HttpClient } from '@angular/common/http'
import { User } from '../models/user.model'
import { IResponse } from '../models/response.model'
import { Router } from '@angular/router'


@Injectable({ providedIn: 'root' })
export class UserService {
  private currentUserSubject = new BehaviorSubject<User | null>(null)
  public currentUser = this.currentUserSubject.asObservable().pipe(distinctUntilChanged())
  public isAuthenticated = this.currentUser.pipe(map(user => !!user))

  constructor(
    private readonly http: HttpClient,
    private readonly jwtService: JwtService,
    private readonly router: Router
  ) {
  }

  login(credentials: { username: string, password: string }): Observable<{ user: User }> {
    return this.http.post<{ response: IResponse }>('/api/v1/users/login', credentials)
      .pipe(
        tap((response: any) => {
          if (response?.success) {
            // let user = response?.data
            let user = response
            if (!user?.avatar){
              user.avatar = 'https://ui-avatars.com/api/?background=008080&color=fff&name=Evn'
            }
            if (!user?.username){
              user.username = 'Admin'
            }
            this.setAuth(user)
          }
        })
      )
  }

  logout(): void {
    this.purgeAuth()
    void this.router.navigateByUrl('/login')
  }

  getCurrentUser(): Observable<{ user: User }> {
    return this.http.get<{ user: User }>('/api/v1/users/profile').pipe(
      tap({
        next: ({ user }) => {this.setAuth(user)},
        error: () => this.purgeAuth()
      }
      ),
      shareReplay(1)
    )
  }

  update(user: Partial<User>): Observable<{ user: User }> {
    return this.http.put<{ user: User }>('/api/v1/users/profile', { user })
      .pipe(tap(({ user }) => {
        this.currentUserSubject.next(user);
      }))
  }

  setAuth(user: User): void {
    if (user?.token){
      this.jwtService.saveToken(user.token)
    }
    this.currentUserSubject.next(user)
  }

  purgeAuth(): void {
    this.jwtService.destroyToken()
    this.currentUserSubject.next(null)
    void this.router.navigateByUrl('/login')
  }

}
