import { render, screen } from "@testing-library/react";
import TranscriptionList from "../TranscriptionList";
import { test, expect } from "@jest/globals";
import React from "react";
import "@testing-library/jest-dom";

test("displays transcription after uploading audio", async () => {
  render(<TranscriptionList />);

  expect(screen.getByText(/transcription/i)).toBeInTheDocument();
});
