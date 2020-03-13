require("dotenv-safe").config();

import rp from "request-promise-native";
import { CookieJar } from "request";

import * as admin from "firebase-admin";
admin.initializeApp({
  credential: admin.credential.cert("firebase-key.json")
});

const output: Array<string> = [];

const STRAND_STRINGS: Array<string> = ["k", "t", "c", "a", "f"];

const STRAND_PRECISION: number = 5
const AVERAGE_PRECISION: number = 10

const TIMEOUT: number = 0.5
const TA_LOGIN_URL: string = "https://ta.yrdsb.ca/yrdsb/index.php"
const TA_COURSE_BASE_URL: string = "https://ta.yrdsb.ca/live/students/viewReport.php"
const TA_ID_REGEX: RegExp = /<a href=\"viewReport.php\?subject_id=([0-9]+)&student_id=([0-9]+)\">/;
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
    other._marks.forEach((v: Mark|null, k: string) => {
      if (v) {
        this._marks.set(k, new Mark(v.numerator, v.denominator, v.weight, v.strand));
      }
    })
  }

  public getMark(strand: string) {
    return this._marks.get(strand)
  }

  get name() {
    return this._name;
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

  get isValid() {
    return this._isValid;
  }

  get name() {
    return this._name;
  }

  get mark() {
    return this._mark;
  }

  get weight() {
    return this._weight;
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
      assessmentList?.forEach((assessment) => {
        this.addAssessment(assessment);
      });
    }
  }

  public equals(other: Course): boolean {
    if (!other || (this._mark != other._mark)) {
      return false;
    }
    STRAND_STRINGS.forEach((strand: string) => {
      if (!this._strands.get(strand)!.equals(other._strands.get(strand)!)) {
        return false;
      }
     });
    return true;
  }

  public generateReport(strandPrecision: number = 3, coursePrecision: number = 4): string {
    let s: string = `${this._name}\n\t`;
    let strandObj: Strand
    STRAND_STRINGS.forEach((strand: string) => {
      strandObj = this._strands.get(strand)!;
      if (strandObj.isValid) {
        s += `${strandObj.name} ${(strandObj.mark*100).toFixed(strandPrecision)} \t`;
      } else {
        s += `${strandObj.name} None \t`;
      }
    });
    if (this._isValid) {
      s += `\n\tavg ${(this._mark*100).toFixed(coursePrecision)}\n\tta shows ${(this._mark*100).toFixed(1)}\n`;
    } else {
      s += "\n\tavg None\n\tta shows None";
    }
    return s;
  }

  public addStrand(strand: string, weight: number): void {
    this._strands.set(strand, new Strand(strand, weight));
  }

  public addAssessment(assessment: Assessment): void {
    this._assessments.push(assessment);
    STRAND_STRINGS.forEach((strand: string) => {
      if (assessment.getMark(strand)) {
        this._strands.get(strand)!.addMark(assessment.getMark(strand)!);
      }
    });
  }

  public hasAssessment(assessment: Assessment): number|Assessment {
    this._assessments.forEach((ownAssessment: Assessment) => {
      if (ownAssessment.equals(assessment)) {
        return Course.PRESENT;
      } else if (ownAssessment.name == assessment.name) {
        return ownAssessment;
      }
    });
    return Course.NOT_PRESENT;
  }

  public removeAssessment(index: number): void {
    this._assessments.splice(index, 1);
  }

  public calculateMark(): void {
    let totalWeight: number = 0;
    let weightedSum: number = 0;

    this._strands.forEach((strand: Strand|null) => {
      if (strand) {
        strand.calculateMark()
        if (strand.isValid) {
          totalWeight += strand.weight;
          weightedSum += strand.mark*strand.weight;
        }
      }
    });

    if (totalWeight == 0) {
      this._isValid = false;
      this._mark = 1.0;
    } else {
      this._isValid = true
      this._mark = weightedSum/totalWeight;
    }
  }

  get assessments() {
    return this._assessments;
  }

  get name() {
    return this._name;
  }
}

function mergeFromInto(taCourse: Course, localCourse: Course): void {
  if (taCourse.equals(localCourse)) {
    return;
  }

  let status: number|Assessment;
  taCourse.assessments.forEach((taAssessment: Assessment) => {
    status = localCourse.hasAssessment(taAssessment);
    // Course.PRESENT: do nothing
    if (status == Course.NOT_PRESENT) {
      localCourse.addAssessment(taAssessment);
      output.push(`added ${taAssessment.name} to ${localCourse.name}`);
    } else if (typeof status != "number") {
      // Course.PRESENT_BUT_DIFFERENT
      (<Assessment>status).copyFrom(taAssessment);
      output.push(`updated ${taAssessment.name}`);
    }
  });

  localCourse.assessments.forEach((localAssignment: Assessment, i: number) => {
    status = taCourse.hasAssessment(localAssignment);
    if (status == Course.NOT_PRESENT) {
      output.push(`removed ${localAssignment.name}`);
      localCourse.removeAssessment(i);
    }
  });
}

function mergeCourseLists(taCourses: Array<Course>, localCourses: Array<Course>): void {
  let taMap = new Map<string, Course>();
  let localMap = new Map<string, Course>();

  taCourses.forEach((course: Course) => {
    taMap.set(course.name, course);
  });
  localCourses.forEach((course: Course) => {
    localMap.set(course.name, course);
  });

  let taNames: Set<string> = new Set<string>(taCourses.map((course: Course): string => course.name));
  let localNames: Set<string> = new Set<string>(localCourses.map((course: Course): string => course.name));

  taNames.forEach((v: string) => {
    if (!localNames.has(v)) {
      output.push(`added ${v} to local courses`);
      localCourses.push(taMap.get(v)!);
    }
  });

  localNames.forEach((v: string) => {
    if (taNames.has(v)) {
      mergeFromInto(taMap.get(v)!, localMap.get(v)!);
    }
  });
}

async function getFromTa(auth: Object): Promise<Array<Course>> {
  output.push("logging in...");
  let session: CookieJar = rp.jar();

  let mainPage: string = await rp.post({
    url: TA_LOGIN_URL,
    jar: session,
    form: auth,
    followAllRedirects: true
  });

  let idMatcher: RegExp = new RegExp(TA_ID_REGEX, "g");

  let courseIDs: RegExpMatchArray|null = idMatcher.exec(mainPage);
  if (!courseIDs) {
    throw new Error("No open reports found"));
  }

  output.push("logged in");
  let courses: Array<Course> = [];

  while (courseIDs) {
    output.push(`getting ${courseIDs[1]}...`);
    rp.get({
      url: TA_COURSE_BASE_URL,
      qs: { subject_id: courseIDs[1], student_id: courseIDs[2] },
      followAllRedirects: false,
      timeout: Number(process.env.TIMEOUT)
    });
    output.push("got report");

    courseIDs = idMatcher.exec(body);
  }
  return courses;
}

getFromTa({username: process.env.USER, password: process.env.PASS});

console.log(output);