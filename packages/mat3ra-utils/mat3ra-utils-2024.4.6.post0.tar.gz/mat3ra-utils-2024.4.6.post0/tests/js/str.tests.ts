import { expect } from "chai";

import { findPreviousVersion } from "../../src/js/shared/str";

describe("findPreviousVersion", () => {
    const versions = ["5.4.2", "3.2", "6.2", "4", "7.2.1"];

    it("should find a previous semantic version", () => {
        const previous = findPreviousVersion(versions, "5.2");
        expect(previous).to.be.equal("4");
    });

    it("should return undefined if no previous version is found", () => {
        const previous = findPreviousVersion(versions, "2");
        // eslint-disable-next-line no-unused-expressions
        expect(previous).to.be.undefined;
    });
});
