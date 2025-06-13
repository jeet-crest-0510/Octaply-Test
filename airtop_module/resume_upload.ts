import { AirtopClient } from "@airtop/sdk";
import path from "path";

const sessionId = process.env.AIRTOP_SESSION_ID!;
const windowId = process.env.AIRTOP_WINDOW_ID!;
const apiKey = process.env.AIRTOP_API_KEY!;
const filePath = process.env.RESUME_FILE_PATH!;

if (!sessionId || !windowId || !apiKey || !filePath) {
  console.error("❌ Missing required environment variables.");
  process.exit(1);
}

const client = new AirtopClient({ apiKey });
// const filePath = path.resolve("D:\\Crest Training\\Octaply\\Airtop AI\\Resumes\\resume.pdf");

console.log("Resolved path to upload file:", filePath);

async function uploadResume(): Promise<void> {
  try {
    console.log("⏳ Uploading and selecting file...");

    const inputResponse = await client.windows.uploadFileAndSelectInput(sessionId, windowId, {
      uploadFilePath: filePath,
      elementDescription: "Resume input file field",
    });

    // if (inputResponse.errors && inputResponse.errors.length > 0) {
    //   console.error("⚠️ File input errors:", inputResponse.errors);
    // } else {
    //   console.log("✅ File uploaded and input set successfully.");
    // }
  } catch (error) {
    if (error instanceof Error) {
      console.error("❌ Error:", error.message);
      console.error("📂 Was looking for file at:", filePath);
    } else {
      console.error("❌ Unknown error:", error);
    }
  }
}

uploadResume().then(() => {
  console.log("🎉 TypeScript script complete.");
  process.exit(0); // ✅ force exit after successful execution
}).catch((err) => {
  console.error("❌ Top-level error:", err);
  process.exit(1); // ❌ exit with error code
});

