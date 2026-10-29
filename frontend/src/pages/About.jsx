import BinVisual from "../components/BinVisual";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";

const BIN_GUIDE = [
  { kind: "red-sack", title: "Red recycling sack", items: "Clean plastics, tins, cans and empty milk cartons.", advice: "Rinse containers before recycling them." },
  { kind: "blue-sack", title: "Blue recycling sack", items: "Clean paper and cardboard, including grease-free pizza boxes.", advice: "Keep it dry. Tissues and greasy cardboard do not belong here." },
  { kind: "food-caddy", title: "Food-waste caddy", items: "Leftover food, peelings and used tea bags in a lined kitchen caddy.", advice: "Move it into the outside food caddy. Never put food waste in recycling or general waste." },
  { kind: "general-waste", title: "General waste", items: "Non-recyclable items such as crisp packets, polystyrene and contaminated packaging.", advice: "Bag it securely and use this only when it cannot be recycled, reused or composted." },
  { kind: "glass-caddy", title: "Glass caddy", items: "Empty glass jars and bottles.", advice: "Remove lids before placing glass in the caddy." },
];

function About() {
  return (
    <div className="page-shell">
      <Navbar />
      <main className="content-layout about-layout">
        <section className="card-surface about-hero">
          <div>
            <span className="badge">About WasteWise AI</span>
            <h1>Better disposal decisions, one image at a time.</h1>
            <p>WasteWise AI is a student project that helps people make a more informed first decision about everyday waste. Upload one image and the service suggests a category, disposal route and guidance.</p>
          </div>
          <div className="about-bin-display" aria-hidden="true">
            {BIN_GUIDE.map((bin) => (
              <BinVisual
                className="about-bin-visual"
                kind={bin.kind}
                key={bin.kind}
                label={bin.title}
              />
            ))}
          </div>
        </section>

        <section className="about-copy-grid">
          <article className="card-surface">
            <p className="eyebrow">How the project works</p>
            <h2>From upload to useful guidance</h2>
            <p>The app sends one image to the authenticated API. Four trained image-classification models assess it, then the backend selects a valid result and returns the suggested disposal route. The browser displays that API response; it does not decide the bin itself.</p>
          </article>
          <article className="card-surface">
            <p className="eyebrow">Limits and privacy</p>
            <h2>Use it as guidance, not a final decision</h2>
            <p>A confidence score is not a guarantee: poor lighting, an unusual angle, similar-looking items, or an item outside the trained categories can lead to an incorrect result. Images are processed to produce a prediction; this project does not present its result as an authoritative council decision. Always follow local labels and official collection guidance when they differ.</p>
          </article>
        </section>

        <section className="bin-guide-section">
          <div className="section-intro">
            <span className="badge">Bin colour guide</span>
            <h2>Know where your waste belongs</h2>
            <p>Cardiff-oriented examples only — collection rules and accepted materials vary by area.</p>
          </div>
          <div className="bin-guide-grid">
            {BIN_GUIDE.map((bin) => (
              <article className="card-surface bin-guide-card" key={bin.kind}>
                <BinVisual
                  className="bin-guide-visual"
                  kind={bin.kind}
                  label={bin.title}
                />
                <h3>{bin.title}</h3>
                <p>{bin.items}</p>
                <p className="bin-advice">{bin.advice}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="card-surface collection-note">
          <p className="eyebrow">Collection days</p>
          <h2>Your collection schedule depends on your address</h2>
          <p>Collection days, frequency and accepted materials differ in every area and can change during holiday periods. Check your local council’s address-based collection calendar before putting containers out.</p>
        </section>
      </main>
      <Footer />
    </div>
  );
}

export default About;
