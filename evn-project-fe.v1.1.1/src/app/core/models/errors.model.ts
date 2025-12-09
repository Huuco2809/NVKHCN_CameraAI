export interface Errors {
  errors: {[key: string]: string};
}

export interface Error {
  code?: number;
  message?: string;
}