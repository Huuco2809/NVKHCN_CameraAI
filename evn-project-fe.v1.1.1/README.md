# EvnProjectFe
This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 15.2.7.

## Change environments
`src/environments/*.ts`
```json
export const environment = {
    production: false,
    title: 'Local Environment',
    apiUrl: 'http://localhost:8030'
};
```
## Development server
Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.
```bash
ng serve --configuration=development
ng serve -c development
```
Or use production config
```bash
ng serve --configuration=production
ng serve -c production
```

## Build
Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Run by Docker
```bash
sudo docker build -f Dockerfile -t dashboard .
sudo docker run -it --init -p 4200:4200 --name dashboard dashboard
```