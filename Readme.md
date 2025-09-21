d# Progress Report (Sep 12, 2025)

## 1. Bidimensional Mental Rotation (BMR)
- **Updated instructions**
  - [TODO] Need estimation of time costs for each section (currently using place holder “lasts about X minutes”)
  - [TODO] Need reversed instructions (saved for later, after agreeing on the final version of the task)
- [TODO] Need new stimuli (in black) (preferably directly edit the `images` folder without changing the sequence, because we do **not** have the python files that generate condition files / sort stimuli images anymore)
- Transition screens between block automatically applied (“Trials completed! …” + “Remember, …”)

## 2. Tridimensional Mental Rotation (TMR)
- **Updated instructions**
  - [TODO] Need estimation of time costs for each section (currently using place holder “lasts about X minutes”)
  - [TODO] Need reversed instructions (saved for later, after agreeing on the final version of the task)

## 3. Actions Prediction (AP)
- **Updated instructions**
  - [TODO] Need estimation of time costs for each section (currently using place holder “lasts about X minutes”)
  - [TODO] Need reversed instructions (saved for later, after agreeing on the final version of the task)
- Transition screens between block automatically applied (“Trials completed! …” + “Remember, …”)
- [TODO] Currently there are no video for test3 / test4 (so no more tests after block 2). Should I select some new ones for them?

## 4. Cognitive Control
- Merged with my version (enabled automatic VERSION selection)
  - Fixed multiple bugs in `motor.py` / `sensorimotor.py` / `contextual.py` / `main.py`
  - Corrected answers for different versions (previously all versions had the same answer)
  - [TODO] Pre-mature error is not treated as an error anymore — is this on purpose or should I fix it?
- [TODO] Need estimation of time costs for each section (currently using place holder “lasts about X minutes”)
- [TODO] Need reversed instructions (saved for later, after agreeing on the final version of the task)

## 5. Tapping
- Directly applied my fixed version from last meeting (should be okay to use!)

## 6. N-back
- Implemented n-back task
- [TODO] Need transition page between 0-1 / 1-2 tasks
- [TODO] 0-back improvements:
  - Have an introduction screen after page 6 saying: next you’ll see the target stimulus for 10 seconds (0_back_introduction.jpg)
  - Have another introduction screen  after showing the target saying: the actual trials will begin in [a countdown for maybe 3 seconds (not too long so that they still remember the stimulus)?] seconds (count_down.jpg)
- [TODO] How do we randomize the trials? We want the answer to be same and different at around 50-50?
- [TODO] Maybe we need a clear instruction at the 1st stimulus for 1-back and first two stimuli for 2-back that the participant should not respond to these as they need to wait for the “back”?

