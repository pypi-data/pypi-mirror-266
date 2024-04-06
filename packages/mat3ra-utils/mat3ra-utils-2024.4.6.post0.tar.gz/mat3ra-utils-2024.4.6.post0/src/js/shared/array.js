import flatten from "lodash/flatten";
import isArray from "lodash/isArray";
import keys from "lodash/keys";
import uniq from "lodash/uniq";

export function safeMakeArray(x) {
    if (!isArray(x)) return [x];
    return x;
}

/**
 * @summary Returns objects array in compact csv format. E.g.:
 * [{a: 1, b: 2}, {a: 2, d: 3}] -> [['a','b','d'],[1, 2, null], [2, null, 3]]
 * @param objects
 */
export function convertToCompactCSVArrayOfObjects(objects) {
    const headers = uniq(flatten(objects.map((x) => keys(x))));
    const result = [headers];
    objects.forEach((x) => {
        const row = [];
        headers.forEach((header) => {
            // eslint-disable-next-line no-prototype-builtins
            row.push(x.hasOwnProperty(header) ? x[header] : null);
        });
        result.push(row);
    });

    return result;
}
