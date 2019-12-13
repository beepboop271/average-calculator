# average-calculator (use ta-access branch for teachassist access)
does stuff with marks: ~~currently only accepts properly formatted text files~~ really really close to getting from teach assist (the hard stuff is all done)

todo:
- gui feat. pygame because thats what we used in grade 10 comp sci and im not learning anything else
- fun hypothetical mark stuff some way better than creating a copy text file and editing it— not sure how this could work without a gui so basically the same as the first point
- %influence of an assignment, existing or upcoming (bc mrs k always goes "THIS QUIZ WILL BE ONLY JUST 0.1% OF YOUR MARK"— we'll see about that)
- what mark do i need to get in x to have y— idk man i want this todo list to appear somewhat interesting

## formatting the data file
COURSE *name-of-the-course*\n\
WEIGHTS *KU-weight* *TI-weight* *C-weight* *A-weight*\n\
*assessment-name* *KU-mark* *TI-mark* *C-mark* *A-mark* *FINAL-mark*\n\
*repeat assessments until done*\n\
\n\
*repeat courses until done*\
note: any amount of whitespace is allowed when listing assessments, see example files
### formatting marks
*numerator*/*denominator* *weight*\
or\
the character 'n' if no mark is given in the strand
### that section was really confusing
just look in the example files you'll get it

## calculation explanation
this application is intended for the following style of mark calculation:

each assignment can have marks from at least 1 of 4 strands: "knowledge+understanding", "thinking+inquiry", "communication", and "application"\
an assignment can also have a mark for the "final" strand\
every single mark for each strand has an individual weight

for example, a math quiz might have 20 marks in knowledge at weight 2 (like multiple choice) and 20 marks in application at weight 2 (for some full solution problem solving questions)

a math test on the other hand might have 15 knowledge at weight 7 (because the test is more important to the final average), 10 communication marks at weight 7, and 20 thinking marks at weight 7

say a student got the following:
```
      K     T     C     A
quiz  17/20 n/a   n/a   19/20
test  15/15 18/20 9/10  n/a
```

as percentages:
```
      K    T    C    A
quiz  85%  n/a  n/a  95%
test  100% 90%  90%  n/a
```

to calculate the student's weighted average for each strand, each percentage is multiplied by its weight and added to the other weighted percentages. the resulting sum is divided by the sum of all the weights to get the weighted average.

e.g.

K: (85% * 2) + (100% * 7) = 870%, 870% / (2+7) ~ 96.7%\
(since there was only one mark for T, C, and A, their weighted average is just that mark)

now that the student has 4 final strand marks, one average needs to be calculated.\
each course will have a different weighting for each strand. for example a science course might have knowledge worth 25% of the final mark with 15% in T, C, and A (and 30% for summatives+exam). whereas a math course could have K and A each worth 25% of the final mark (since being able to do and apply the math is more important) and T and C worth 15% of the final mark.

so each strand weighted average is then multiplied by the strand weight, and the sum of each weighted strand is the final average

e.g. for the math course:
```
K (30%) T (15%) C (15%) A (40%)
96.7%   90%     90%     95%
```

final = (96.7% * 30%) + (90% * 15%) + (90% * 15%) + (95% * 40%)\
final ~ 94%
