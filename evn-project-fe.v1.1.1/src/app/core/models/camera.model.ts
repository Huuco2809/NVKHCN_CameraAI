export interface Camera {
    camera_id: string;
    camera_name: string;
    rtsp: string;
    thumbnail: string;
    socket_url: string;
    showing: boolean;
    have_object: boolean;
    tracking: boolean;
    regions: any;
}
