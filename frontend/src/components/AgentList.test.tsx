import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import AgentList from "./AgentList";

vi.mock("../api", () => ({
  api: {
    getAgents: vi.fn(),
  },
}));

import { api } from "../api";
const mockGetAgents = vi.mocked(api.getAgents);

describe("AgentList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("렌더링", () => {
    it("제목이 표시된다", async () => {
      mockGetAgents.mockResolvedValueOnce([]);
      render(<AgentList />);
      expect(screen.getByText(/Agents/)).toBeInTheDocument();
    });

    it("에이전트가 없으면 빈 상태 메시지가 표시된다", async () => {
      mockGetAgents.mockResolvedValueOnce([]);
      render(<AgentList />);
      await waitFor(() => {
        expect(screen.getByText("No agents registered")).toBeInTheDocument();
      });
    });
  });

  describe("에이전트 표시", () => {
    it("에이전트 목록을 표시한다", async () => {
      mockGetAgents.mockResolvedValueOnce([
        {
          id: 1,
          name: "be-developer",
          description: "Backend developer",
          model: "sonnet",
          skills: ["python"],
          status: "active",
        },
        {
          id: 2,
          name: "fe-developer",
          description: "Frontend developer",
          model: "sonnet",
          skills: ["typescript"],
          status: "active",
        },
      ]);

      render(<AgentList />);

      await waitFor(() => {
        expect(screen.getByText("be-developer")).toBeInTheDocument();
      });
      expect(screen.getByText("fe-developer")).toBeInTheDocument();
      expect(screen.getByText("2")).toBeInTheDocument();
    });

    it("에이전트 상세 정보를 표시한다", async () => {
      mockGetAgents.mockResolvedValueOnce([
        {
          id: 1,
          name: "researcher",
          description: "Research analyst",
          model: "opus",
          skills: ["research"],
          status: "pending",
        },
      ]);

      render(<AgentList />);

      await waitFor(() => {
        expect(screen.getByText("researcher")).toBeInTheDocument();
      });
      expect(screen.getByText("opus")).toBeInTheDocument();
      expect(screen.getByText("Research analyst")).toBeInTheDocument();
    });
  });

  describe("상태 색상", () => {
    it("active 상태는 success 클래스를 가진다", async () => {
      mockGetAgents.mockResolvedValueOnce([
        {
          id: 1,
          name: "test",
          description: "test",
          model: "sonnet",
          skills: [],
          status: "active",
        },
      ]);

      render(<AgentList />);

      await waitFor(() => {
        const status = screen.getByText("active");
        expect(status.className).toContain("text-success");
      });
    });

    it("pending 상태는 warning 클래스를 가진다", async () => {
      mockGetAgents.mockResolvedValueOnce([
        {
          id: 1,
          name: "test",
          description: "test",
          model: "sonnet",
          skills: [],
          status: "pending",
        },
      ]);

      render(<AgentList />);

      await waitFor(() => {
        const status = screen.getByText("pending");
        expect(status.className).toContain("text-warning");
      });
    });

    it("rejected 상태는 error 클래스를 가진다", async () => {
      mockGetAgents.mockResolvedValueOnce([
        {
          id: 1,
          name: "test",
          description: "test",
          model: "sonnet",
          skills: [],
          status: "rejected",
        },
      ]);

      render(<AgentList />);

      await waitFor(() => {
        const status = screen.getByText("rejected");
        expect(status.className).toContain("text-error");
      });
    });
  });

  describe("에러 처리", () => {
    it("API 에러 시 빈 상태를 표시한다", async () => {
      mockGetAgents.mockRejectedValueOnce(new Error("500"));
      render(<AgentList />);

      await waitFor(() => {
        expect(screen.getByText("No agents registered")).toBeInTheDocument();
      });
    });
  });
});
