import { FSharpResult$2 } from "../../tests/Thoth.Json.JavaScript.Tests/fable_modules/fable-library.4.5.0/Choice.js";
import { fromValue } from "../Thoth.Json.Core/Decode.fs.js";

export const helpers = {
    isString(jsonValue) {
        return typeof jsonValue === "string";
    },
    isNumber(jsonValue_1) {
        return (typeof jsonValue_1) === "number";
    },
    isBoolean(jsonValue_2) {
        return typeof jsonValue_2 === "boolean";
    },
    isNullValue(jsonValue_3) {
        return jsonValue_3 == null;
    },
    isArray(jsonValue_4) {
        return Array.isArray(jsonValue_4);
    },
    isObject(jsonValue_5) {
        return jsonValue_5 === null ? false : (Object.getPrototypeOf(jsonValue_5 || false) === Object.prototype)
                ;
    },
    isUndefined(jsonValue_6) {
        return (typeof jsonValue_6) === "undefined";
    },
    isIntegralValue(jsonValue_7) {
        return isFinite(jsonValue_7) && Math.floor(jsonValue_7) === jsonValue_7
                    ;
    },
    asString(jsonValue_8) {
        return jsonValue_8;
    },
    asBoolean(jsonValue_9) {
        return jsonValue_9;
    },
    asArray(jsonValue_10) {
        return jsonValue_10;
    },
    asFloat(jsonValue_11) {
        return jsonValue_11;
    },
    asFloat32(jsonValue_12) {
        return jsonValue_12;
    },
    asInt(jsonValue_13) {
        return jsonValue_13;
    },
    getObjectKeys(jsonValue_14) {
        return Object.keys(jsonValue_14);
    },
    getField(fieldName, jsonValue_15) {
        return jsonValue_15[fieldName];
    },
    anyToString(jsonValue_16) {
        return JSON.stringify(jsonValue_16, null, 4) + ''
                    ;
    },
};

export function fromString(decoder, value) {
    try {
        return fromValue(helpers, "$", decoder, JSON.parse(value));
    }
    catch (matchValue) {
        if (matchValue instanceof SyntaxError) {
            return new FSharpResult$2(1, ["Given an invalid JSON: " + matchValue.message]);
        }
        else {
            throw matchValue;
        }
    }
}

