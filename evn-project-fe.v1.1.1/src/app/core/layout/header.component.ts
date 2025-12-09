import {Component, inject} from '@angular/core'
import {UserService} from '../services/user.service'
import {RouterLink, RouterLinkActive} from '@angular/router'
import {AsyncPipe, NgIf} from '@angular/common'
import {ShowAuthedDirective} from '../../shared/show-authed.directive'

@Component({
  selector: 'app-layout-header',
  templateUrl: './header.component.html',
  imports: [
    RouterLinkActive,
    RouterLink,
    AsyncPipe,
    NgIf,
    ShowAuthedDirective
  ],
  standalone: true
})

 
export class HeaderComponent {
  currentUser$ = inject(UserService).currentUser
  public clock: any;
  constructor(
    private readonly userService: UserService,
  ) {
  }

  logout(): void {
    this.userService.logout()
  }

  getCurrentTime(): string {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    
    return `${hours}:${minutes}:${seconds}`;
  }
  
 
  
  ngOnInit() {
    setInterval(() => {
       this.clock = this.getCurrentTime();
      // console.log(this.clock);  
    }, 1000);
  }
  
}
