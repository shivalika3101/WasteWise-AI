import FeatureCard from "../components/FeatureCard";
import Footer from "../components/Footer";
import Hero from "../components/Hero";
import Navbar from "../components/Navbar";

function Home() {
  return (
    <>
      <Navbar />
      <Hero />

      <section className="how">
        <h2>How WasteWise AI Works</h2>

        <div className="steps">
          <div>
            <span className="step-icon">1</span>
            <h3>Register or Sign In</h3>
            <p>Authenticate once and your session is restored on refresh.</p>
          </div>

          <div>
            <span className="step-icon">2</span>
            <h3>Upload One Image</h3>
            <p>Preview the file in-browser, then submit it without sending a user ID.</p>
          </div>

          <div>
            <span className="step-icon">3</span>
            <h3>Review the Result</h3>
            <p>See category, confidence, bin, guidance, and the prediction ID clearly.</p>
          </div>
        </div>
      </section>

      <section className="features">
        <h2>Milestone Features</h2>

        <div className="cards">
          <FeatureCard
            icon="Secure"
            title="Authenticated upload"
            description="Protected routes keep profile and prediction pages behind sign-in."
          />
          <FeatureCard
            icon="Restore"
            title="Restored auth state"
            description="Saved bearer tokens are validated and used to restore the session."
          />
          <FeatureCard
            icon="Preview"
            title="Single-image preview"
            description="Users can preview exactly one file before submitting it."
          />
          <FeatureCard
            icon="Result"
            title="Clear result states"
            description="Loading, error, and final prediction details are surfaced in the UI."
          />
        </div>
      </section>

      <Footer />
    </>
  );
}

export default Home;
