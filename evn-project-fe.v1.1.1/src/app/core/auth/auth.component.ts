import {Component, OnDestroy, OnInit} from '@angular/core'
import {
  Validators,
  FormGroup,
  FormControl,
  ReactiveFormsModule
} from '@angular/forms'
import {ActivatedRoute, Router, RouterLink} from '@angular/router'
import {NgIf} from '@angular/common'
import {ErrorComponent} from '../../shared/error.component'
import {Error} from '../models/error.model'
import {UserService} from '../services/user.service'
import {takeUntil} from 'rxjs/operators'
import {Subject} from 'rxjs'

interface AuthForm {
  password: FormControl<string>
  username: FormControl<string>
}

@Component({
  selector: 'app-auth-page',
  templateUrl: './auth.component.html',
  imports: [
    RouterLink,
    NgIf,
    ErrorComponent,
    ReactiveFormsModule
  ],
  standalone: true
})
export class AuthComponent implements OnInit, OnDestroy {
  title = 'Đăng nhập'
  error: Error = {}
  isSubmitting = false
  authForm: FormGroup<AuthForm>
  destroy$ = new Subject<void>()

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly userService: UserService,
  ) {
    this.authForm = new FormGroup<AuthForm>({
      username: new FormControl('', {
        validators: [Validators.required],
        nonNullable: true
      }),
      password: new FormControl('', {
        validators: [Validators.required],
        nonNullable: true
      })
    })
  }

  ngOnInit(): void {
  }

  ngOnDestroy() {
    this.destroy$.next()
    this.destroy$.complete()
  }

  submitForm(): void {
    this.isSubmitting = true
    this.error = {}

    let observable = this.userService.login(this.authForm.value as {username: string, password: string})

    observable.pipe(
      takeUntil(this.destroy$)
    ).subscribe({
        next: () => this.router.navigateByUrl('/'),
        error: err => {
          this.error = err
          this.isSubmitting = false
        }
      }
    )
  }
}
