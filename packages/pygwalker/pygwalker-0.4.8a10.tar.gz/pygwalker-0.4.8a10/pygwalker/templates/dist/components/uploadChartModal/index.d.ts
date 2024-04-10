import React from "react";
import type { IGWHandler } from "@kanaries/graphic-walker/interfaces";
import type { VizSpecStore } from '@kanaries/graphic-walker/store/visualSpecStore';
interface IUploadChartModal {
    gwRef: React.MutableRefObject<IGWHandler | null>;
    storeRef: React.MutableRefObject<VizSpecStore | null>;
    open: boolean;
    dark: string;
    setOpen: (open: boolean) => void;
}
declare const UploadChartModal: React.FC<IUploadChartModal>;
export default UploadChartModal;
