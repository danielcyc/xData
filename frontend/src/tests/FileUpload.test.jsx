import { screen, render, fireEvent } from "@testing-library/react";
import { test, expect } from "@jest/globals";
import React from "react";
import FileUpload from "../FileUpload";
import "@testing-library/jest-dom";

test("renders file upload input", () => {
  render(<FileUpload />);
  const fileInput = screen.getByRole("button", {
    name: /upload and transcribe/i,
  });
  expect(fileInput).toBeInTheDocument();
});

test("uploads a file successfully", () => {
  render(<FileUpload />);

  const fileInput = screen.getByRole("button", {
    name: /upload and transcribe/i,
  });
  const file = new File(["dummy content"], "audio_sample.mp3", {
    type: "audio/mpeg",
  });

  fireEvent.change(fileInput, { target: { files: [file] } });

  expect(fileInput.files[0].name).toBe("audio_sample.mp3");
});
