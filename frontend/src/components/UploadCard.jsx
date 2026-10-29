import { motion } from "framer-motion";

function UploadCard({ title, text, primaryLabel, secondaryLabel, onPrimary, onSecondary }) {
  return (
    <motion.div
      className="upload-box"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.35 }}
      transition={{ duration: 0.45 }}
    >
      <div className="upload-icon" aria-hidden="true">
        <span></span>
      </div>
      <h3>{title}</h3>
      <p>{text}</p>
      <div className="upload-actions">
        <button type="button" className="upload-btn" onClick={onPrimary}>
          {primaryLabel}
        </button>
        <button type="button" className="ghost-btn upload-ghost-btn" onClick={onSecondary}>
          {secondaryLabel}
        </button>
      </div>
    </motion.div>
  );
}

export default UploadCard;
