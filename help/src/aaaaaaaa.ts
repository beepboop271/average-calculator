require("dotenv-safe").config();

import * as admin from "firebase-admin"
admin.initializeApp({
  credential: admin.credential.cert("firebase-key.json")
});

const output: Array<string> = [];

const STRAND_STRINGS: Array<string> = ["k", "t", "c", "a", "f"];

const STRAND_PRECISION: number = 5
const AVERAGE_PRECISION: number = 10

const TIMEOUT: number = 0.5
const TA_LOGIN_URL: string = "https://ta.yrdsb.ca/yrdsb/"
const TA_COURSE_BASE_URL: string = "https://ta.yrdsb.ca/live/students/viewReport.php"
const TA_ID_REGEX: RegExp = /<a href=\"viewReport.php\?subject_id=([0-9]+)&student_id=([0-9]+)\">/
const _STRAND_PATTERNS: Array<RegExp> = [
  /<td bgcolor=\"ffffaa\" align=\"center\" id=\"\S+?\">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)<\/font> <\/td>/,
  /<td bgcolor=\"c0fea4\" align=\"center\" id=\"\S+?\">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)<\/font> <\/td>/,
  /<td bgcolor=\"afafff\" align=\"center\" id=\"\S+?\">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)<\/font> <\/td>/,
  /<td bgcolor=\"ffd490\" align=\"center\" id=\"\S+?\">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)<\/font> <\/td>/,
  /<td bgcolor=\"#?dedede\" align=\"center\" id=\"\S+?\">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)<\/font> <\/td>/
]


class Mark {
  private _numerator: number;
  private _denominator: number;
  private _weight: number;
  private _strand: string;
  private _decimal: number;

  constructor(numerator: number, denominator: number, weight: number,
              strand: string) {
    this._numerator = numerator;
    this._denominator = denominator;
    this._weight = weight;
    this._strand = strand;
    this._decimal = numerator/denominator;
  }

  public equals(other: Mark): boolean {
    return (other
            && (this._numerator == other._numerator)
            && (this._denominator == other._denominator)
            && (this._weight == other._weight)
            && (this._strand == other._strand));
  }

  public toString(): string {
    return `Mark(${this._strand} W${this._weight} ${this._numerator}/${this._denominator} ${(this._decimal*100).toFixed(2)})`;
  }

  get strand() {
    return this._strand;
  }
  get weight() {
    return this._weight;
  }
  get numerator() {
    return this._numerator;
  }
  get denominator() {
    return this._denominator;
  }
}

class Assessment {
  private _name: string;
  private _marks: Map<string, Mark|null>;

  constructor(name: string, marks: Array<Mark>|null = null) {
    this._name = name;
    this._marks = new Map([
      ["k", null],
      ["t", null],
      ["c", null],
      ["a", null],
      ["f", null]
    ]);

    marks?.forEach((mark: Mark) => {
      if (mark) {
        this.addMark(mark);
      }
    });
  }

  public equals(other: Assessment): boolean {
    if (!other || (this._name != other._name)) {
      return false;
    }
    this._marks.forEach((v: Mark|null, k: string) => {
      if (v != other._marks.get(k)) {
        return false;
      }
    });
    return true;
  }

  public toString(): string {
    return `Assessment(${this._name}: K:${this._marks.get("k")} T:${this._marks.get("t")} C:${this._marks.get("c")} A:${this._marks.get("a")} F:${this._marks.get("f")})`;
  }

  public addMark(mark: Mark): void {
    this._marks.set(mark.strand, mark);
  }

  public copyFrom(other: Assessment): void {
    this._marks = other._marks;
  }
}

class Strand {
  private _name: string;
  private _weight: number;
  private _marks: Array<Mark>;
  private _mark: number;
  private _isValid: boolean;

  constructor(strand: string, weight: number) {
    this._name = strand;
    this._weight = weight;
    this._marks = [];
    this._mark = 1.0;
    this._isValid = false;
  }

  public equals(other: Strand): boolean {
    if (!other
        || (this._name != other._name)
        || (this._mark != other._mark)
        || (this._marks.length != other._marks.length)
        || (this._weight != other._weight)) {
      return false;
    }
    // rip O(n^2)
    this._marks.forEach((mark: Mark) => {
      if (!other.hasMark(mark)) {
        return false;
      }
    });
    return true;
  }

  public addMark(mark: Mark): void {
    this._marks.push(mark);
  }

  public hasMark(mark: Mark): boolean {
    this._marks.forEach((ownMark: Mark) => {
      if (ownMark.equals(mark)) {
        return true;
      }
    });
    return false;
  }

  public calculateMark(): void {
    let totalWeight: number = 0;
    let weightedSum: number = 0;

    this._marks.forEach((mark: Mark) => {
      totalWeight += mark.weight;
      weightedSum += (mark.numerator/mark.denominator)*mark.weight;
    });

    if (totalWeight == 0) {
      this._isValid = false;
      this._mark = 1.0;
    } else {
      this._isValid = true;
      this._mark = weightedSum/totalWeight;
    }
  }
}

class Course {
  public static readonly NOT_PRESENT: number = 1;
  public static readonly PRESENT_BUT_DIFFERENT: number = 2;
  public static readonly PRESENT: number = 3;

  private _name: string;
  private _assessments: Array<Assessment>;
  private _mark: number;
  private _isValid: boolean;
  private _strands: Map<string, Strand|null>;

  constructor(name: string, weights: Array<number> = [], assessmentList: Array<Assessment>|null = null) {
    this._name = name;
    this._assessments = [];
    this._mark = 1.0;
    this._isValid = false;
    this._strands = new Map([
      ["k", null],
      ["t", null],
      ["c", null],
      ["a", null],
      ["f", null]
    ]);
    if (weights.length == this._strands.size) {
      weights.forEach((weight: number, i: number) => {
        this.addStrand(STRAND_STRINGS[i], weight);
      });
    }
  }

  public addStrand(strand: string, weight: number): void {
    this._strands.set(strand, new Strand(strand, weight));
  }
}