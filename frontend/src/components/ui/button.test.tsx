import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Button } from "./button";

describe("Button", () => {
  it("renders with text", () => {
    render(<Button>Click me</Button>);
    expect(
      screen.getByRole("button", { name: "Click me" }),
    ).toBeInTheDocument();
  });

  it("handles click events", async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await userEvent.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("renders different variants", () => {
    const { rerender } = render(<Button variant="destructive">Delete</Button>);
    expect(screen.getByRole("button")).toHaveAttribute(
      "data-variant",
      "destructive",
    );

    rerender(<Button variant="outline">Cancel</Button>);
    expect(screen.getByRole("button")).toHaveAttribute(
      "data-variant",
      "outline",
    );
  });

  it("renders as child element with asChild", () => {
    render(
      <Button asChild>
        <a href="/test">Link</a>
      </Button>,
    );
    expect(screen.getByRole("link", { name: "Link" })).toBeInTheDocument();
  });

  it("is disabled when disabled prop is true", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
