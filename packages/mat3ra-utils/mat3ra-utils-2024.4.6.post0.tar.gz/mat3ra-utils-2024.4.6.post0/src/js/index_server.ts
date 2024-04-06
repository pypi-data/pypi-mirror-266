import { sharedUtils } from "./index";
import * as file from "./server/file";

export const serverUtils = {
    file,
};

export const Utils = {
    ...sharedUtils,
    ...serverUtils,
};
export default { ...Utils };
