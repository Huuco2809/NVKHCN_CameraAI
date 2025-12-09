// data.service.ts

import { Injectable } from '@angular/core';
import { CameraStatistics } from '../../core/models/camera-statistic.model';
@Injectable({
  providedIn: 'root',
})
export class DataService {

  analyzeData_2(data: any[]): any {
    const result = {
      person: [],
      vehicle: [],
      animal: []
    };

    const uniqueCameraNames = new Set<string>();

    data.forEach(item => {
      const cameraName = item.camera_name;
      if (item.cls_name == 'person') {
        result.person.push(cameraName);
        uniqueCameraNames.add(cameraName);
      } else if ((item.cls_name == 'car' || item.cls_name == 'truck' || item.cls_name == 'bus')) {
        result.vehicle.push(cameraName);
        uniqueCameraNames.add(cameraName);
      } else if ((item.cls_name == 'dog' || item.cls_name == 'cat' || item.cls_name == 'cow' || item.cls_name === 'horse')) {
        result.animal.push(cameraName);
        uniqueCameraNames.add(cameraName);
      }
    });
    result.person.sort();
    result.vehicle.sort();
    result.animal.sort();
    const modifiedZ = this.removeDuplicateCameras(result);
    return modifiedZ;
  }


  analyzeData_1(data: any):any {
    let cameraStatisticsMap: Record<string, CameraStatistics> = {};

    for (const cameraName in data) {
      if (data.hasOwnProperty(cameraName)) {
        const categories = data[cameraName];

        let personCount = 0;
        let animalCount = 0;
        let vehicleCount = 0;
        let totalInArea = 0;
        let goIn: boolean[] = [];
        let positions: string[] = [];

        for (const category in categories) {
          if (categories.hasOwnProperty(category)) {
            const objects = categories[category];

            // Increment the count based on the category
            if (category === 'person') {
              personCount += objects.length;
            } else if (category === 'dog'||category === 'cat'||category === 'cow') {
              animalCount += objects.length;
            } else if (category === 'car'||category === 'truck'||category === 'bus') {
              vehicleCount += objects.length;
            }

            // Accumulate in_area, go_in, and position counts
            for (const obj of objects) {
              totalInArea += obj.in_area ? 1 : 0;
              goIn.push(obj.go_in || false);
              positions.push(obj.position || 'N/A');
            }
          }
        }
        // Update or add to the map
        cameraStatisticsMap[cameraName] = {
          cameraName,
          personCount,
          animalCount,
          vehicleCount,
          totalInArea,
          goIn,
          positions,
        };
      }
    }

    // Convert the map values to an array
    const res = Object.values(cameraStatisticsMap);
    return res;
  }

  groupObjectsByCameraName(objects: any[]): any {
    const groupedObjects = {};
    objects.forEach((object) => {
      const cameraName = object.camera_name;

      if (groupedObjects.hasOwnProperty(cameraName)) {
        groupedObjects[cameraName].push(object);
      } else {
        groupedObjects[cameraName] = [object];
      }
    });

    return groupedObjects;
  }


  groupClsNameByCamera(data: any): any {
    const groupedData = {};

    for (const cameraName in data) {
      if (data.hasOwnProperty(cameraName)) {
        const objects = data[cameraName];
        const groupedObjects = {};

        objects.forEach((object: any) => {
          const clsName = object.cls_name;

          if (groupedObjects.hasOwnProperty(clsName)) {
            groupedObjects[clsName].push({
              camera_id: object.camera_id,
              camera_name: object.camera_name,
              thumbnail: object.thumbnail,
              in_area: object.in_area,
              go_in: object.go_in,
              go_out: object.go_out,
              position: object.position
            });
          } else {
            groupedObjects[clsName] = [{
              camera_id: object.camera_id,
              camera_name: object.camera_name,
              thumbnail: object.thumbnail,
              in_area: object.in_area,
              go_in: object.go_in,
              go_out: object.go_out,
              position: object.position
            }];
          }
        });

        groupedData[cameraName] = groupedObjects;
      }
    }

    return groupedData;
  }



  removeDuplicateCameras(data: Record<string, any>): Record<string, any> {
    try {
        // Remove duplicate occurrences within each category
        for (const key in data) {
            if (Array.isArray(data[key])) {
                data[key] = [...new Set(data[key])];
            }
        }

        return data;
    } catch (error) {
        // Handle processing errors
        console.error("Error processing data:", error);
        return {}; // Return an empty object in case of an error
    }
}




}
