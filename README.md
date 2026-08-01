# IAT461-Final -- Client : Manmeet

**Link to Dataset:** https://www.kaggle.com/datasets/ulasozdemir/wildfires-in-canada-19502021

## Entity: BC Wildfire Service (BCWS)

BC Wildfire Service is the government agency in British Columbia that handles wildfire prevention and firefighting across the province. They manage fire crews, aircraft, and equipment used to detect and put out fires each year. After some of the worst fire seasons on record in 2017, 2018, and 2021, the agency has a limited budget and needs to decide where to focus its resources instead of spreading them evenly across the whole province every season.

## Problem Definition

BC Wildfire Service has a limited budget each year and is looking at three ways to spend it.

1. **Option A:** Hire more firefighting crews and buy more aircraft.

2. **Option B:** Build more fire detection towers and cameras across the province.

3. **Option C:** Use fire records from 2002 to 2021 to predict whether a newly reported fire is more likely caused by people or by lightning, based on where and when it started. This would help

BCWS send the right kind of prevention effort, like public fire bans and patrols in areas prone to human caused fires, or early detection resources in areas prone to lightning caused fires, before the fire season gets bad.

First, look at the past fire data (location, season, size, and cause) from 2002 to 2021 to check whether hiring more crews or building more towers is actually backed up by what the data shows, or if targeting prevention smarter (Option C) is the better use of money.

If **Option C** turns out to be the right path, build a model that predicts whether a newly reported fire is more likely human caused or lightning caused, using its location, season, and ecozone.

## Stakeholder / Audience

The people who will use this are the fire prevention planners at BC Wildfire Service. Each spring, before fire season starts, they decide where to send patrols, where to put up public fire bans, and which areas need better lightning detection.

Right now they mostly spread this evenly across regions. A model that flags whether new fires in a region tend to be human caused or lightning caused would help them plan differently by area.

## Success Criteria

A good answer is a model that can flag whether a newly reported fire is more likely human caused or lightning caused, using its location, season, and ecozone, well enough that prevention planners would actually trust it to guide where they send patrols and fire ban notices.

It should be especially good at catching human caused fires, since those are the ones prevention efforts can actually stop. If the model just repeats what planners already assume (for example, "cities have more human caused fires"), that would not be useful. It needs to point to specific regions or seasons where the current assumptions are wrong.
