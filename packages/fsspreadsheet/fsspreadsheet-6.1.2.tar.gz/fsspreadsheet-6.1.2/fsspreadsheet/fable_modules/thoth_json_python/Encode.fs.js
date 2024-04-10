import { defaultOf } from "../../tests/Thoth.Json.JavaScript.Tests/fable_modules/fable-library.4.5.0/Util.js";
import { toJsonValue } from "../Thoth.Json.Core/Encode.fs.js";
import { some } from "../../tests/Thoth.Json.JavaScript.Tests/fable_modules/fable-library.4.5.0/Option.js";

export const helpers = {
    encodeString(value) {
        return value;
    },
    encodeChar(value_1) {
        return value_1;
    },
    encodeFloat(value_2) {
        return value_2;
    },
    encodeFloat32(value_3) {
        return value_3;
    },
    encodeBool(value_4) {
        return value_4;
    },
    encodeNull() {
        return defaultOf();
    },
    createEmptyObject() {
        return {};
    },
    setPropertyOnObject(o, key, value_5) {
        o[key] = value_5;
    },
    encodeArray(values) {
        return Array.from(values);
    },
    encodeList(values_1) {
        return Array.from(values_1);
    },
    encodeSeq(values_2) {
        return Array.from(values_2);
    },
    encodeSBtye(value_6) {
        return value_6;
    },
    encodeByte(value_7) {
        return value_7;
    },
    encodeInt16(value_8) {
        return value_8;
    },
    encodeUInt16(value_9) {
        return value_9;
    },
    encodeInt(value_10) {
        return value_10;
    },
    encodeUInt32(value_11) {
        return value_11;
    },
};

export function toString(space, value) {
    const json = toJsonValue(helpers, value);
    return JSON.stringify(json, void 0, some(space));
}

