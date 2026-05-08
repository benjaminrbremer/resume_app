# resume_app
An app that tracks job applications, skills, and experience, and provides quick and easy resume and cover letter tailoring through a natural language interface. Easily showcase the best side of you in each application, without tedious manual rewriting.

## Project Motivation and Goal

This project had a few motivations:
- I need a solution for tailoring my own resume for job applications
- I have experience integrating GenAI into applications, but always in the cloud, and for technical data. I wanted to be able to use some clever information retrieval and prompt engineering to get something to work on my machine locally
- A major part of any job these days is being able to use AI tools for coding. This project would take way too long for me to complete 100% on my own. I also don't have frontend development experience. But, with tools like Claude Code out there, that's not an excuse for not being able to tackle projects like this. Using AI tools to help with this project has a couple benefits:
  - I get experience with the tools I will be using in the real world, that school never taught me how to use. I can fail now, so that I can succeed at my job later
  - I get to demonstrate my ability to harness these tools to deliver solutions quickly, even in tasks I haven't done before
  - I am a hands-on learner. Instead of spending weeks learning a technology before implementing anything, I get to learn-as-I-go, leading to both faster learning, and faster delivery of solutions

The goal of this project is to have a web application that stores a user's experience (education, personal projects, work, etc.), tracks job applications, and uses information retrieval and an LLM to generate tailored resumes for each application.

## Current Progress

To the current point, I have developed the frontend and backend in parallel. I had thorough design specs for the database and API, and generated a UI on top of that to be able to test. Unfortunately, that structure is leading to a lot of problems. First, too many things are changing at once. Then, when something breaks, it's hard to tell what actually broke. Second, when something I hadn't considered comes to mind, it's hard to propogate updates to the backend all the way through.

The current state is something that looks nice, and sort of works. It will gather your experience, and track applications. The LLM is being a bit finnicky, mostly due to me only being able to run a small model. 

The current state is also relatively future-proof. I have intentionally designed it so that, even though the LLM runs locally, using OLlama, it uses a very similar API to OpenAI - meaning that cloud deployment would be as easy as changing the target of the request. Furthermore, the database operations are designed in a way that the database could be migrated to any database system, the functions updated according to that system's syntax, and everything's off to the races.

## Future Work

As I mentioned, my biggest mistake was building too fast, without designing first. This is a critical error when using AI tools for coding. Each step may be right, but putting them all together can cause some weird interactions. The immediate next step I want to take is a thorough review and update of design specifications in multiple phases, with intense verification at each phase:
- Phase 1: Database schema and operations
  - Ensure all relevant fields exist, are the correct type, and have the correct contraints
  - Ensure all operations (creating new user, logging in, adding new experience, adding new application, etc.) all work 
- Phase 2: Helper functions (information retrieval)
  - My experience has taught me that good data fixes most issues with the reliability of LLM responses. So, I will be using helper functions to get all the relevant data for resume generation
  - Retrieving relevant experience: this will be done through vector search. It will be tested by making sure that all relevant experience and only relevant experience is retrieved
  - Company research: I want to be able to note some important information about the company the user is applying to. This step will be a combination of web scraping, and using an LLM to summarize the results, in the context of what is important to note for a job application
  - Compression of job description: job descriptions contain a lot of stuff that doesn't inform what needs to be on the resume. To keep context length down, an LLM will first be used to extract key details about the job decription
- Phase 3: LLM prompting for resume generation
  - Hopefully, using clearly-defined and well-tested helper functions will help improve this step automatically
  - To further improve accuracy, I will dive into prompt engineering 
  - I would love to test the output with anoher LLM as a judge - it may be hard to get this to work very well since I can only run small models, but it's important to know how to evaluate GenAI agents
- Phase 4: Frontend
  - Now that all of the backend is known to work, developing a clean frontend is a breeze

Note that in this new structure, no feature is built before everything it is dependent on is complete and thoroughly tested. This means that (ideally), nothing from an earlier phase should break during development of a later phase. If it does, or I decide to add a new feature or specification, I add it to the earlier stage first, confirm it works, then continue developing the later stage. 
