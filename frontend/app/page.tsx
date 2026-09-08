import { MenuScreen } from "@/components/menu-screen";
import { getMenu } from "@/lib/menu-api";

export default async function HomePage() {
  const menu = await getMenu();
  return <MenuScreen {...menu} />;
}
