import { Injectable } from '@angular/core';
import {MatDialog, MatDialogRef} from '@angular/material/dialog';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { SelectionDialogComponent } from './selection-dialog.component';
@Injectable()
export class SelectionDialogService {
  constructor(private dialog: MatDialog) { }
  dialogRef: MatDialogRef<SelectionDialogComponent>;
  
  public open(options: { title: any; message: any; cancelText: any; confirmText: any; placeholder: any; items: any}) {
    this.dialogRef = this.dialog.open(SelectionDialogComponent, {    
         data: {
           title: options.title,
           message: options.message,
           placeholder: options.placeholder,
           items: options.items,
           cancelText: options.cancelText,
           confirmText: options.confirmText
         }
    });
  }
  public confirmed(): Observable<any> {
    
    return this.dialogRef.afterClosed().pipe(take(1), map(res => {
        return res;
      }
    ));
  }
}
