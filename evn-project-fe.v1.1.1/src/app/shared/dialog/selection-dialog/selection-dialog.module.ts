import { ChangeDetectionStrategy, Component, HostListener, Inject, Output, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { MatDialog, MAT_DIALOG_DATA, MatDialogRef } from "@angular/material/dialog";
import { NgForOf } from '@angular/common';
// import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import {MatSelectChange} from '@angular/material/select';

@Component({
changeDetection: ChangeDetectionStrategy.OnPush,
selector: 'app-selection-dialog',
templateUrl: './selection-dialog.component.html',
imports: [
  NgForOf
],
styles: [`
  .header, .dialog-message {
      text-transform: lowercase;
  }
  .header::first-letter, .dialog-message::first-letter {
      text-transform: uppercase;
  }
  .btn-cancel {
      background-color: red;
      color: #fff;
  }
`],
standalone: true,
schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class SelectionDialogComponent {
  
  constructor(@Inject(MAT_DIALOG_DATA) public data: {
                  cancelText: string,
                  confirmText: string,
                  placeholder: string,
                  items: any,
                  message: string,
                  title: string
              }, private mdDialogRef: MatDialogRef<SelectionDialogComponent>) { }
  value: string = ''
  action: boolean = false

  public cancel() {
    this.action = false
    this.close({value: this.value, action: this.action})
  }

  public close(value:any) {
    this.mdDialogRef.close(value)
  }

  public confirm() {
    this.action = true
    this.close({value: this.value, action: this.action})
  }
  
  @HostListener("keydown.esc") 
  public onEsc() {
    this.action = false
    this.close({value: this.value, action: this.action})
  }

  selectedChange(e: any) {
    console.log(e)
    this.value = e.value
    this.mdDialogRef.close(this.value)
  }
  onChange(e: any) {
    this.value = e?.target?.value
  }
}