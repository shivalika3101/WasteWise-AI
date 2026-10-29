import Footer from "../components/Footer";
import Navbar from "../components/Navbar";

const STEPS = [
  {
    title: "1. Sign in and choose one image",
    text: "Use a clear JPG or PNG image of one waste item. The upload page accepts files up to 5 MB. Good lighting and a single, visible item make the result easier to interpret.",
  },
  {
    title: "2. Upload and review the result",
    text: "WasteWise returns the predicted waste category, a confidence percentage, a suggested disposal route, guidance, and the prediction ID. The suggested bin comes from the API, not from a browser guess.",
  },
  {
    title: "3. Interpret confidence carefully",
    text: "Confidence describes how strongly the classification system supported its result for that image; it is not a guarantee. If the image is blurry, unusual, or contains several items, check the item and local guidance before disposing of it.",
  },
  {
    title: "4. Complete the bin check",
    text: "Select the local container you think is right. The backend checks your answer against the stored recommendation and gives clear correct or incorrect feedback. An incorrect answer can be tried again.",
  },
];

function HowTo() {
  return (
    <div className="page-shell">
      <Navbar />
      <main className="content-layout howto-layout">
        <section className="card-surface learn-hero">
          <span className="badge">How to use WasteWise</span>
          <h1>From one photo to a better disposal decision.</h1>
          <p>Use this as a practical guide, then follow the labels and collection instructions for your area.</p>
        </section>
        <section className="howto-steps" aria-label="How to use WasteWise">
          {STEPS.map((step) => (
            <article className="card-surface howto-step" key={step.title}>
              <h2>{step.title}</h2>
              <p>{step.text}</p>
            </article>
          ))}
        </section>
      </main>
      <Footer />
    </div>
  );
}

export default HowTo;
