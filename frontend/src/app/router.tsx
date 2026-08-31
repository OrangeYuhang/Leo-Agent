import { createBrowserRouter } from "react-router";
import RootLayout from "./layouts/RootLayout";
import App from "./routes/app";
import Stack from "./routes/stack";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        path: "/",
        element: <App />,
      },
      {
        path: "/stack",
        element: <Stack />,
      },
    ],
  },
]);
