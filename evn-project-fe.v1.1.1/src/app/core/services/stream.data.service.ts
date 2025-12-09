import { Injectable } from '@angular/core';
import { webSocket } from 'rxjs/webSocket';
import { Observable, timer, Subject, EMPTY } from 'rxjs';
import { retryWhen, tap, delayWhen, switchAll, catchError } from 'rxjs/operators';
export const RECONNECT_INTERVAL = 2000;


// @Injectable({
//   providedIn: 'root' //enable singleton pattern
// })
@Injectable()
export class StreamDataService {

  public socket$: any;
  // private messagesSubject$ = new Subject();
  // public messages$ = this.messagesSubject$.pipe(switchAll(), catchError(e => { throw e }));

  constructor() {
  }

  /**
   * Creates a new WebSocket subject and send it to the messages subject
   * @param cfg if true the observable will be retried.
   */
  public connect(url: string, cfg: { reconnect: boolean } = { reconnect: false }): void {

    if ((!this.socket$ || this.socket$.closed) && url) {
      this.socket$ = this.getNewWebSocket(url);
      // this.socket$.asObservable().subscribe((event:any) => {
      //   // console.log('data', event?.data)
      // });
      // const messages = this.socket$.pipe(cfg.reconnect ? this.reconnect : (o:any) => o,
      //   tap({
      //     error: error => console.log(error),
      //   }), catchError(_ => EMPTY))
      // //toDO only next an observable if a new subscription was made double-check this
      // this.messagesSubject$.next(messages);
    }
  }

  /**
   * Retry a given observable by a time span
   * @param observable the observable to be retried
   */
  private reconnect(observable: Observable<any>): Observable<any> {
    return observable.pipe(retryWhen(errors => errors.pipe(tap(val => console.log('[Data Service] Try to reconnect', val)),
      delayWhen(_ => timer(RECONNECT_INTERVAL)))));
  }

  close() {
    if (this.socket$){
      this.socket$.complete();
      this.socket$ = undefined;
    }
  }

  sendMessage(msg: any) {
    this.socket$.next(msg);
  }

  /**
   * Return a custom WebSocket subject which reconnects after failure
   */
  private getNewWebSocket(url: string) {
    return webSocket({
      url: url,
      binaryType: 'arraybuffer',
      deserializer: (e) => e,
      openObserver: {
        next: () => {
          // console.log('[StreamDataService]: connection ok');
        }
      },
      closeObserver: {
        next: () => {
          // console.log('[StreamDataService]: connection closed');
          this.socket$ = undefined;
          this.connect(url, { reconnect: true });
        }
      },
    });
  }

  ngOnDestroy(){
    this.close()
  }

}