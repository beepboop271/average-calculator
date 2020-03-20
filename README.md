# average-calculator

does stuff with marks\
now in python 3\
also no more dumb typing text files, teachassist stuff is completely done\
also notifications and whatnot are being developed in https://github.com/beepboop271/average-calculator-v2 because it is significantly different from this python program. you can also use the typescript version there instead of the python script if you want, the only re al difference is that the typescript one explains errors more.

todo:

- fun hypothetical mark stuff some way better than creating a copy text file and editing it— not sure how this could work without a gui so basically the same as the first point
- %influence of an assignment, existing or upcoming (bc mrs k always goes "THIS QUIZ WILL BE ONLY JUST 0.1% OF YOUR MARK"— we'll see about that)
- what mark do i need to get in x to have y— idk man i want this todo list to appear somewhat interesting

## unnecessarily long calculation explanation

### tl;dr: it's just a weighted average

this application is intended for the following style of mark calculation:

each assignment can have marks from at least 1 of 5 strands: "knowledge+understanding", "thinking+inquiry", "communication", "application", and "final". every single mark for each strand has an individual weight

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

```
K: (85% * 2) + (100% * 7) = 870%
             870% / (2+7) ~ 96.7%
```

(since there was only one mark for T, C, and A, their weighted average is just that mark)

now that the student has 4 final strand marks, one average needs to be calculated. each course will have a different weighting for each strand. for example a science course might have knowledge worth 25% of the final mark with 15% in T, C, and A (and 30% for summatives+exam). whereas a math course could have K and A each worth 25% of the final mark (since being able to do and apply the math is more important) and T and C worth 15% of the final mark.

so each strand weighted average is then multiplied by the strand weight, and the sum of each weighted strand is the final average

e.g. for the math course:

```
K (30%) T (15%) C (15%) A (40%)
96.7%   90%     90%     95%

final = (96.7% * 30%) + (90% * 15%) + (90% * 15%) + (95% * 40%)
final ~ 94%
```
