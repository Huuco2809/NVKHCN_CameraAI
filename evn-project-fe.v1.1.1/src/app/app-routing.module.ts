import {inject, NgModule} from '@angular/core';
import {Routes, RouterModule, PreloadAllModules} from '@angular/router';
import {UserService} from './core/services/user.service';
import {map} from 'rxjs/operators';
import {AuthGuard} from "./auth.guard"

const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/camera/camera.component').then(m => m.CameraComponent),
    // canActivate: [() => inject(UserService).isAuthenticated]
    canActivate: [AuthGuard]
  },
  {
    path: 'login',
    loadComponent: () => import('./core/auth/auth.component').then(m => m.AuthComponent),
    canActivate: [() => inject(UserService).isAuthenticated.pipe(map(isAuth => !isAuth))]
  },
  {
    path: 'configs',
    loadComponent: () => import('./features/configs/configs.component').then(m => m.ConfigsComponent),
    canActivate: [AuthGuard]
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {
    preloadingStrategy: PreloadAllModules
  })],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
