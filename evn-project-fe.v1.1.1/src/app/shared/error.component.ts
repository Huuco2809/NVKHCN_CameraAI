import {Component, Input} from '@angular/core';
import {Error} from '../core/models/errors.model';
import {NgForOf, NgIf} from '@angular/common';

@Component({
  selector: 'app-error',
  templateUrl: './error.component.html',
  imports: [
    NgIf,
    NgForOf
  ],
  standalone: true
})
export class ErrorComponent {
  err: string = '';

  @Input() set error(err: Error) {
    this.err = err?.message || '';
  }
}
