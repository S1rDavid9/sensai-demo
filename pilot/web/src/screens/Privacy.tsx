import { Link } from "react-router-dom";

export default function Privacy() {
  return (
    <main className="privacy">
      <h1 className="brand">Sens<span>AI</span> privacy policy</h1>
      <p className="muted">For learners, their parents or guardians, and teachers. Last updated 17 November 2026.</p>

      <section className="card stack">
        <h2>1. A grown-up says yes first, and so do you</h2>
        <p>
          Nobody can use SensAI until a parent or guardian has signed a consent form and you have said
          you want to take part. The researcher has to tick both boxes before a session can start.
          You can stop at any time, and nothing bad will happen if you do.
        </p>
      </section>

      <section className="card stack">
        <h2>2. We do not ask for your name</h2>
        <p>
          You get a code like P01 instead of your name. SensAI never asks for your name, age, school,
          photo or contact details. The list that matches codes to names stays on paper with the researcher.
        </p>
      </section>

      <section className="card stack">
        <h2>3. What SensAI saves</h2>
        <p>
          Your answers, how long each question takes, when you ask for a hint, how many keys you press
          and delete, when you leave the page, and your answer to "How is it going?". This helps the
          researcher understand when learners need help. SensAI does not use your camera or microphone.
        </p>
      </section>

      <section className="card stack">
        <h2>4. Who can see it</h2>
        <p>
          Only the researcher, with a private key. Teachers who help with observing only see the
          observer screen and cannot see answers, scores or the computer's choices. SensAI has no
          adverts, does not sell data and does not send it to other companies.
        </p>
      </section>

      <section className="card stack">
        <h2>5. What the computer decides</h2>
        <p>
          In the school study, the computer's choices were saved for the researcher but never changed
          what learners saw. In this demo, the computer may pick your next puzzle, and safety rules stop
          it from making choices a teacher would not make.
        </p>
      </section>

      <section className="card stack">
        <h2>6. How long it is kept</h2>
        <p>
          Data from the school study is kept until 31 October 2027 and then deleted. This demo only uses
          made-up data, and everything in it is wiped every time the demo restarts.
        </p>
      </section>

      <p className="muted">
        Questions? Ask your teacher to contact the researcher, Akachi David Nwanze, African Leadership
        University, Kigali.
      </p>
      <Link to="/">Back to the start</Link>
    </main>
  );
}
