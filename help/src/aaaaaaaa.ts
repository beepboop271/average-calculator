require("dotenv-safe").config();

import rp from "request-promise-native";
import { CookieJar } from "request";

import * as admin from "firebase-admin";
admin.initializeApp({
  credential: admin.credential.cert("firebase-key.json")
});

const output: string[] = [];

// const STRAND_STRINGS: readonly string[] = ["k", "t", "c", "a", "f"];

const TA_LOGIN_URL: string = "https://ta.yrdsb.ca/yrdsb/index.php";
const TA_COURSE_BASE_URL: string = "https://ta.yrdsb.ca/live/students/viewReport.php";
const TA_ID_REGEX: RegExp = /<a href="viewReport.php\?subject_id=([0-9]+)&student_id=([0-9]+)">/;
const _STRAND_PATTERNS: readonly RegExp[] = [
  /<td bgcolor="ffffaa" align="center" id="\S+?">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size="-2">weight=([0-9\.]+)<\/font> <\/td>/,
  /<td bgcolor="c0fea4" align="center" id="\S+?">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size="-2">weight=([0-9\.]+)<\/font> <\/td>/,
  /<td bgcolor="afafff" align="center" id="\S+?">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size="-2">weight=([0-9\.]+)<\/font> <\/td>/,
  /<td bgcolor="ffd490" align="center" id="\S+?">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size="-2">weight=([0-9\.]+)<\/font> <\/td>/,
  /<td bgcolor="#?dedede" align="center" id="\S+?">([0-9\.]+) \/ ([0-9\.]+).+?<br> <font size="-2">weight=([0-9\.]+)<\/font> <\/td>/
];


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

  public equals(other: Mark|null): boolean {
    return (
      other != null
      && this._numerator == other._numerator
      && this._denominator == other._denominator
      && this._weight == other._weight
      && this._strand == other._strand
    );
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

class Stranded<T> implements Iterable<[string, T|null]> {
  private static readonly strands: string[] = ["k", "t", "c", "a", "f"];
  private static readonly strandSet: Set<string> = new Set(Stranded.strands);

  private data: Map<string, T|null>;

  constructor(
    k: T|null = null,
    t: T|null = null,
    c: T|null = null,
    a: T|null = null,
    f: T|null = null
  ) {
    this.data = new Map<string, T | null>([
      ["k", k],
      ["t", t],
      ["c", c],
      ["a", a],
      ["f", f]
    ]);
  }

  public [Symbol.iterator](): Iterator<[string, T|null]> {
    let idx: number = 0;
    return {
      next: () => {
        if (idx < 5) {
          return {value: [Stranded.strands[idx], this.data.get(Stranded.strands[idx])!], done: false};
        } else {
          return {value: undefined, done: true};
        }
      }
    }
  }

  public get(strand: string): T|null {
    if (!Stranded.strandSet.has(strand)) {
      return null;
    }
    return this.data.get(strand)!;
  }

  public set(strand: string, element: T|null): void {
    if (!Stranded.strandSet.has(strand)) {
      return;
    }
    this.data.set(strand, element);
  }
}

class Assessment implements Iterable<[string, Mark|null]> {
  private _name: string;
  private _marks: Stranded<Mark>;

  constructor(name: string, marks: readonly Mark[]|null = null) {
    this._name = name;

    if (marks != null) {
      this._marks = new Stranded<Mark>(...marks);
    } else {
      this._marks = new Stranded<Mark>();
    }
  }

  public equals(other: Assessment|null): boolean {
    if ((other == null) || (this._name != other._name)) {
      return false;
    }

    for (let [strand, mark] of this._marks) {
      if (mark == null) {
        if (other._marks.get(strand) != null) {
          return false;
        }
      } else if (!mark.equals(other._marks.get(strand)!)) {
        return false;
      }
    }

    return true;
  }

  public toString(): string {
    return `Assessment(${this._name}: K:${this._marks.get("k")} T:${this._marks.get("t")} C:${this._marks.get("c")} A:${this._marks.get("a")} F:${this._marks.get("f")})`;
  }

  public addMark(mark: Mark): void {
    this._marks.set(mark.strand, mark);
  }

  public copyFrom(other: Assessment): void {
    for (let [k, v] of other._marks) {
      if (v) {
        this._marks.set(k, new Mark(v.numerator, v.denominator, v.weight, v.strand));
      }
    }
  }

  public getMark(strand: string) {
    return this._marks.get(strand);
  }

  public [Symbol.iterator](): Iterator<[string, Mark|null]> {
    return this._marks[Symbol.iterator]();
  }

  get name() {
    return this._name;
  }
}

class Strand {
  private _name: string;
  private _weight: number;
  private _marks: Mark[];
  private _mark: number;
  private _isValid: boolean;

  constructor(strand: string, weight: number) {
    this._name = strand;
    this._weight = weight;
    this._marks = [];
    this._mark = 1.0;
    this._isValid = false;
  }

  public equals(other: Strand|null): boolean {
    if (
      (other == null)
      || (this._name != other._name)
      || (this._mark != other._mark)
      || (this._marks.length != other._marks.length)
      || (this._weight != other._weight)
    ) {
      return false;
    }
    // rip O(n^2)
    for (let mark of this._marks) {
      if (!other.hasMark(mark)) {
        return false;
      }
    }
    return true;
  }

  public addMark(mark: Mark): void {
    this._marks.push(mark);
  }

  public hasMark(mark: Mark): boolean {
    for (let ownMark of this._marks) {
      if (ownMark.equals(mark)) {
        return true;
      }
    }
    return false;
  }

  public calculateMark(): void {
    let totalWeight: number = 0;
    let weightedSum: number = 0;

    for (let mark of this._marks) {
      totalWeight += mark.weight;
      weightedSum += (mark.numerator/mark.denominator)*mark.weight;
    }

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
  private _assessments: Assessment[];
  private _mark: number;
  private _isValid: boolean;
  // private _strands: Map<string, Strand | null>;
  private _strands: Stranded<Strand>;

  constructor(
    name: string,
    weights: readonly number[] = [],
    assessmentList: readonly Assessment[] | null = null
  ) {
    this._name = name;
    this._assessments = [];
    this._mark = 1.0;
    this._isValid = false;
    this._strands = new Stranded<Strand>()

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
      assessmentList?.forEach(assessment => {
        this.addAssessment(assessment);
      });
    }
  }

  public equals(other: Course|null): boolean {
    if ((other == null) || (this._mark != other._mark)) {
      return false;
    }

    for (let [strandStr, strand] of this._strands) {
      if (strand == null) {
        if (other._strands.get(strandStr) != null) {
          return false;
        }
      } else {
        if (!strand.equals(other._strands.get(strandStr))) {
          return false;
        }
      }
    }
    return true;
  }

  public generateReport(precision: number = 4): string {
    let s: string = `${this._name}\n\t`;

    for (let [strandStr, strand] of this._strands) {
      if ((strand != null) && strand.isValid) {
        s += `${strandStr} ${(strand.mark*100).toFixed(precision)} \t`;
      } else {
        s += `${strandStr} None \t`;
      }
    }

    if (this._isValid) {
      s += `\n\tavg ${(this._mark*100).toFixed(precision)}\n\tta shows ${(this._mark*100).toFixed(1)}\n`;
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
    for (let a of assessment.s) {

    }

    for (let strand of STRAND_STRINGS) {
      if (assessment.getMark(strand) != null) {
        if (this._strands.get(strand) != null) {
          this._strands.get(strand)!.addMark(assessment.getMark(strand)!);
        } else {
          throw new Error("Tried to add to nonexistent strand");
        }
      }
    }
  }

  public hasAssessment(assessment: Assessment): number | Assessment {
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

    this._strands.forEach((strand: Strand | null) => {
      if (strand) {
        strand.calculateMark();
        if (strand.isValid) {
          totalWeight += strand.weight;
          weightedSum += strand.mark * strand.weight;
        }
      }
    });

    if (totalWeight == 0) {
      this._isValid = false;
      this._mark = 1.0;
    } else {
      this._isValid = true;
      this._mark = weightedSum / totalWeight;
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

function mergeCourseLists(taCourses: readonly Course[], localCourses: Course[]): void {
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

interface IAuthMap {
  username: string,
  password: string
}

async function getFromTa(auth: IAuthMap): Promise<Course[]> {
  output.push("logging in...");
  let session: CookieJar = rp.jar();

  let homePage: string = await rp.post({
    url: TA_LOGIN_URL,
    jar: session,
    form: auth,
    followAllRedirects: true,
    timeout: Number(process.env.TIMEOUT)
  });

  let idMatcher: RegExp = new RegExp(TA_ID_REGEX, "g");

  let courseIDs: RegExpMatchArray|null = idMatcher.exec(homePage);
  if (!courseIDs) {
    output.push("No open reports found");
    throw new Error("No open reports found");
  }

  output.push("logged in");
  let courses: Course[] = [];

  let report: string;
  let name: string|null;
  let weights: number[]|null;
  let assessments: Assessment[]|null;
// console.log(report);

  while (courseIDs) {
    output.push(`getting ${courseIDs[1]}...`);
    report = await rp.get({
      url: TA_COURSE_BASE_URL,
      jar: session,
      qs: { subject_id: courseIDs[1], student_id: courseIDs[2] },
      followAllRedirects: false,
      timeout: Number(process.env.TIMEOUT)
    });
    output.push("got report");

    report = report.replace(/\s+/g, " ");

    name = getName(report);
    if (name != null) {
      console.log(name);
      weights = getWeights(report);

      if (weights != null) {
        console.log(weights);
        assessments = getAssessments(report);

        if (assessments != null) {
          courses.push(new Course(name, weights, assessments));
        } else {
          output.push("Course assessments not found");
          // throw new Error("Course assessments not found");
        }
      } else {
        output.push("Course weights not found");
        // throw new Error("Course weights not found");
      }
    } else {
      output.push("Course name not found");
      // throw new Error("Course name not found");
    }
    // console.log(report.substring(idMatcher.lastIndex));
    courseIDs = idMatcher.exec(homePage);
    // console.log(courseIDs);
  }
  return courses;
}

function getName(report: string): string|null {
  const match: RegExpExecArray|null = /<h2>(\S+?)<\/h2>/.exec(report);
  if (match) {
    return match[1];
  } else {
    return null;
  }
}

function getWeights(report: string): number[]|null {
  const idx: number = report.indexOf("#ffffaa");
  if (idx == -1) {
    return null;
  }
  report = report.slice(idx, idx+800);

  let weightTable: string[] = report.split("#");
  weightTable.shift();

  let weights: number[] = [];
  for (let i: number = 0; i < 4; ++i) {
    weights.push(Number(
      weightTable[i]
        .substring(weightTable[i].indexOf("%"))
        .match(/([0-9\.]+)%/)![1]
    ));
  }
  return weights;
}

function getAssessments(report: string): Assessment[]|null {
  let assessmentTable: ITagMatch|null = getEndTag(
    report,
    /table border="1" cellpadding="3" cellspacing="0" width="100%"/,
    /(<table)|(<\/table>)/,
    "<table"
  );
  if (assessmentTable == null) {
    return null;
  }

  report = assessmentTable.content;

  return null;
}

interface ITagMatch {
  content: string,
  next: string
};

function getEndTag(report: string, beginningPattern: RegExp, searchPattern: RegExp, startTag: string): ITagMatch|null {
  let match: RegExpMatchArray|null = report.match(beginningPattern);
  if (match == null) {
    return null;
  }
  let idx: number = match.index!;

  let tagsToClose: number = 1;
  let searcher: RegExp = new RegExp(searchPattern, "g");

  while (tagsToClose > 0) {
    match = searcher.exec(report.substring(idx+1));
    if (match == null) {
      return null;
    }
    if (match[0] == startTag) {
      ++tagsToClose;
    } else {
      --tagsToClose;
    }
  }

  return {
    content: report.slice(idx-1, idx+match.index!+match[0].length),
    next: report.substring(idx+match.index!+match[0].length)
  };
}

getFromTa({
  username: process.env.USER!,
  password: process.env.PASS!
}).then(() => console.log(output));

// console.log(output);