# SensAI: research demo

Public demo deployment of the SensAI web application. The full project (simulator, training, analysis and report material) is at https://github.com/S1rDavid9/SensAI_capstone.

SensAI is a research prototype from an ALU BSc Software Engineering capstone project by Akachi David Nwanze. It estimates a learner's behavioural state (on task, rushing, struggling or stuck) from interaction data after every answer, and a Deep Q-Network trained in simulation, constrained by rule-based guardrails, chooses a support action.

**This is a demonstration with invented data. It is not for use with children.** The database is empty when the service starts and is wiped on every restart. No data from the pilot study is included.

- Learner screen: `/learn` (needs a session code created on the researcher screen)
- Observer screen: `/observe` (observer key)
- Researcher screen: `/researcher` (researcher key)

Both models (the Stage 1 classifier and the DQN) run inside this container.

## Running it

The app runs as one Docker container that serves the web app, the API and both models. It needs two environment variables, `PILOT_RESEARCHER_KEY` and `PILOT_OBSERVER_KEY`; the container refuses to start without them. It listens on `$PORT` (default 7860).

```bash
docker build -t sensai-demo .
docker run -p 7860:7860 -e PILOT_RESEARCHER_KEY=... -e PILOT_OBSERVER_KEY=... sensai-demo
```

On Render: New → Web Service → this repository, language Docker, free instance, and set the two keys as environment variables.
