import type { IChartExportResult } from '@kanaries/graphic-walker/interfaces';
export declare function download(data: string, filename: string, type: string): void;
export declare function formatExportedChartDatas(chartData: IChartExportResult): Promise<any>;
export declare function getTimezoneOffsetSeconds(): number;
