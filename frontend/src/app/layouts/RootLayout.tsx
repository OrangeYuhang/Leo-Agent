import { Outlet } from "react-router";
import VersionInfo from "@/components/VersionInfo";

export default function RootLayout() {
  return (
    <>
      <Outlet />
      <VersionInfo />
    </>
  );
}
