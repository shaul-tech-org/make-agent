import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the title", () => {
    render(<App />);
    expect(screen.getByText("shaul-custom-agent")).toBeInTheDocument();
  });

  it("renders the dashboard subtitle", () => {
    render(<App />);
    expect(
      screen.getByText("Coordinator Pattern Multi-Agent Dashboard")
    ).toBeInTheDocument();
  });

  it("renders the request section", () => {
    render(<App />);
    expect(screen.getByText("Request")).toBeInTheDocument();
  });

  it("renders the agents section", () => {
    render(<App />);
    expect(screen.getByPlaceholderText("요청을 입력하세요...")).toBeInTheDocument();
  });
});
