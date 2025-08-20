import React, { useState, useEffect } from "react";

// Restaurant Profit Manager
// Single-file React component designed to be previewed in the canvas.
// Uses Tailwind utility classes for styling. Persist data to localStorage.
// Features:
// - Menu item management (name, price, cost, inventory)
// - Order builder (create orders from menu)
// - Revenue, COGS, Gross Profit, Expenses, Net Profit calculation
// - Daily summary with list of orders
// - Quick features: add sample data, export CSV, reset day

export default function RestaurantProfitManager() {
  // Menu items
  const [menu, setMenu] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("rpm_menu")) || [];
    } catch (e) {
      return [];
    }
  });

  // Orders for the day
  const [orders, setOrders] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("rpm_orders")) || [];
    } catch (e) {
      return [];
    }
  });

  // Expense list (name + amount)
  const [expenses, setExpenses] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("rpm_expenses")) || [];
    } catch (e) {
      return [];
    }
  });

  // UI states for creating/editing
  const [editingItem, setEditingItem] = useState(null);
  const [orderCart, setOrderCart] = useState([]);

  useEffect(() => {
    localStorage.setItem("rpm_menu", JSON.stringify(menu));
  }, [menu]);

  useEffect(() => {
    localStorage.setItem("rpm_orders", JSON.stringify(orders));
  }, [orders]);

  useEffect(() => {
    localStorage.setItem("rpm_expenses", JSON.stringify(expenses));
  }, [expenses]);

  // ----- Menu helpers -----
  function addMenuItem(item) {
    setMenu((m) => [...m, { id: Date.now(), ...item }]);
  }

  function updateMenuItem(id, patch) {
    setMenu((m) => m.map((it) => (it.id === id ? { ...it, ...patch } : it)));
  }

  function removeMenuItem(id) {
    setMenu((m) => m.filter((it) => it.id !== id));
  }

  // ----- Orders -----
  function addToCart(itemId) {
    setOrderCart((c) => {
      const found = c.find((x) => x.itemId === itemId);
      if (found) return c.map((x) => (x.itemId === itemId ? { ...x, qty: x.qty + 1 } : x));
      return [...c, { itemId, qty: 1 }];
    });
  }

  function changeCartQty(itemId, qty) {
    if (qty <= 0) return setOrderCart((c) => c.filter((x) => x.itemId !== itemId));
    setOrderCart((c) => c.map((x) => (x.itemId === itemId ? { ...x, qty } : x)));
  }

  function clearCart() {
    setOrderCart([]);
  }

  function placeOrder(note = "") {
    if (orderCart.length === 0) return;
    const orderItems = orderCart.map((c) => {
      const item = menu.find((m) => m.id === c.itemId);
      return {
        name: item.name,
        price: Number(item.price),
        cost: Number(item.cost),
        qty: c.qty,
        itemId: item.id,
      };
    });
    const subtotal = orderItems.reduce((s, it) => s + it.price * it.qty, 0);
    const cogs = orderItems.reduce((s, it) => s + it.cost * it.qty, 0);
    const order = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      items: orderItems,
      subtotal,
      cogs,
      note,
    };

    // decrement inventory if present
    setMenu((m) =>
      m.map((it) => {
        const ordered = orderItems.find((o) => o.itemId === it.id);
        if (!ordered) return it;
        if (typeof it.inventory === "number") {
          return { ...it, inventory: Math.max(0, it.inventory - ordered.qty) };
        }
        return it;
      })
    );

    setOrders((o) => [order, ...o]);
    clearCart();
  }

  // ----- Calculations -----
  const totalRevenue = orders.reduce((s, o) => s + o.subtotal, 0);
  const totalCOGS = orders.reduce((s, o) => s + o.cogs, 0);
  const grossProfit = totalRevenue - totalCOGS;
  const totalExpenses = expenses.reduce((s, e) => s + Number(e.amount || 0), 0);
  const netProfit = grossProfit - totalExpenses;

  // ----- Utility / CSV export -----
  function exportOrdersCSV() {
    const rows = [
      ["orderId", "ts", "item", "price", "cost", "qty", "subtotal", "cogs"],
    ];
    orders.forEach((o) => {
      o.items.forEach((it) =>
        rows.push([o.id, o.timestamp, it.name, it.price, it.cost, it.qty, o.subtotal, o.cogs])
      );
    });
    const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `orders_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // quick seed
  function seedSample() {
    const sample = [
      { id: 1, name: "Chicken Burger", price: 7.5, cost: 3.0, inventory: 50 },
      { id: 2, name: "Fries", price: 3.0, cost: 0.6, inventory: 200 },
      { id: 3, name: "Coke", price: 1.5, cost: 0.2, inventory: 100 },
    ];
    setMenu(sample);
    setOrders([]);
    setExpenses([]);
  }

  function resetDay() {
    if (!confirm("Reset today's orders and expenses? This won't delete the menu.")) return;
    setOrders([]);
    setExpenses([]);
  }

  // ----- Expense helpers -----
  function addExpense(name, amount) {
    setExpenses((e) => [...e, { id: Date.now(), name, amount: Number(amount) }]);
  }

  function removeExpense(id) {
    setExpenses((e) => e.filter((x) => x.id !== id));
  }

  // ----- Compact components inside single file -----
  function MenuEditor() {
    const [name, setName] = useState("");
    const [price, setPrice] = useState("");
    const [cost, setCost] = useState("");
    const [inventory, setInventory] = useState("");

    useEffect(() => {
      if (editingItem) {
        setName(editingItem.name);
        setPrice(editingItem.price);
        setCost(editingItem.cost);
        setInventory(editingItem.inventory ?? "");
      } else {
        setName("");
        setPrice("");
        setCost("");
        setInventory("");
      }
    }, [editingItem]);

    function submit(e) {
      e.preventDefault();
      const payload = { name: name.trim(), price: Number(price), cost: Number(cost) };
      if (inventory !== "") payload.inventory = Number(inventory);
      if (editingItem) {
        updateMenuItem(editingItem.id, payload);
        setEditingItem(null);
      } else {
        addMenuItem(payload);
      }
      setName("");
      setPrice("");
      setCost("");
      setInventory("");
    }

    return (
      <form onSubmit={submit} className="p-4 bg-white rounded-2xl shadow-md">
        <h3 className="text-lg font-semibold mb-3">Add / Edit Menu Item</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          <input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="p-2 border rounded" />
          <input required value={price} onChange={(e) => setPrice(e.target.value)} placeholder="Price (sale)" type="number" step="0.01" className="p-2 border rounded" />
          <input required value={cost} onChange={(e) => setCost(e.target.value)} placeholder="Cost (COGS)" type="number" step="0.01" className="p-2 border rounded" />
          <input value={inventory} onChange={(e) => setInventory(e.target.value)} placeholder="Inventory (optional)" type="number" className="p-2 border rounded" />
        </div>
        <div className="mt-3 flex gap-2">
          <button className="px-4 py-2 rounded-2xl shadow hover:shadow-lg">{editingItem ? "Update" : "Add Item"}</button>
          {editingItem && (
            <button type="button" onClick={() => setEditingItem(null)} className="px-4 py-2 rounded-2xl border">Cancel</button>
          )}
        </div>
      </form>
    );
  }

  function MenuList() {
    return (
      <div className="bg-white p-4 rounded-2xl shadow-md">
        <h3 className="text-lg font-semibold mb-3">Menu</h3>
        <div className="space-y-2 max-h-64 overflow-auto">
          {menu.length === 0 && <div className="text-sm text-muted-foreground">No menu items — add some or click sample.</div>}
          {menu.map((it) => (
            <div key={it.id} className="flex items-center justify-between p-2 rounded border">
              <div>
                <div className="font-semibold">{it.name}</div>
                <div className="text-sm">Price: ${Number(it.price).toFixed(2)} • Cost: ${Number(it.cost).toFixed(2)}</div>
                {typeof it.inventory === "number" && <div className="text-xs">Inventory: {it.inventory}</div>}
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => addToCart(it.id)} className="px-3 py-1 rounded-2xl border">Add</button>
                <button onClick={() => setEditingItem(it)} className="px-3 py-1 rounded-2xl border">Edit</button>
                <button onClick={() => removeMenuItem(it.id)} className="px-3 py-1 rounded-2xl border">Delete</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  function CartPanel() {
    return (
      <div className="bg-white p-4 rounded-2xl shadow-md">
        <h3 className="text-lg font-semibold mb-3">Order Cart</h3>
        <div className="space-y-2">
          {orderCart.length === 0 && <div className="text-sm">Cart is empty — add items from the menu.</div>}
          {orderCart.map((c) => {
            const item = menu.find((m) => m.id === c.itemId);
            if (!item) return null;
            return (
              <div key={c.itemId} className="flex items-center justify-between border p-2 rounded">
                <div>
                  <div className="font-semibold">{item.name}</div>
                  <div className="text-sm">${Number(item.price).toFixed(2)} x {c.qty} = ${(item.price * c.qty).toFixed(2)}</div>
                </div>
                <div className="flex items-center gap-2">
                  <input className="w-16 p-1 border rounded" type="number" value={c.qty} onChange={(e) => changeCartQty(c.itemId, Number(e.target.value))} />
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-3 flex gap-2">
          <button onClick={() => placeOrder()} className="px-4 py-2 rounded-2xl shadow">Place Order</button>
          <button onClick={clearCart} className="px-4 py-2 rounded-2xl border">Clear</button>
        </div>
      </div>
    );
  }

  function SummaryPanel() {
    return (
      <div className="bg-white p-4 rounded-2xl shadow-md">
        <h3 className="text-lg font-semibold mb-3">Today's Summary</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="p-2 rounded border">
            <div className="text-xs">Revenue</div>
            <div className="text-xl font-bold">${totalRevenue.toFixed(2)}</div>
          </div>
          <div className="p-2 rounded border">
            <div className="text-xs">COGS</div>
            <div className="text-xl font-bold">${totalCOGS.toFixed(2)}</div>
          </div>
          <div className="p-2 rounded border">
            <div className="text-xs">Gross Profit</div>
            <div className="text-xl font-bold">${grossProfit.toFixed(2)}</div>
          </div>
          <div className="p-2 rounded border">
            <div className="text-xs">Expenses</div>
            <div className="text-xl font-bold">${totalExpenses.toFixed(2)}</div>
          </div>
          <div className="col-span-2 p-2 rounded border bg-slate-50">
            <div className="text-xs">Net Profit</div>
            <div className="text-2xl font-extrabold">${netProfit.toFixed(2)}</div>
          </div>
        </div>
        <div className="mt-3 flex gap-2">
          <button onClick={exportOrdersCSV} className="px-4 py-2 rounded-2xl">Export Orders CSV</button>
          <button onClick={resetDay} className="px-4 py-2 rounded-2xl border">Reset Day</button>
          <button onClick={seedSample} className="px-4 py-2 rounded-2xl border">Seed Sample</button>
        </div>
      </div>
    );
  }

  function OrdersList() {
    return (
      <div className="bg-white p-4 rounded-2xl shadow-md">
        <h3 className="text-lg font-semibold mb-3">Orders ({orders.length})</h3>
        <div className="space-y-2 max-h-64 overflow-auto">
          {orders.map((o) => (
            <div key={o.id} className="p-2 rounded border">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-semibold">Order {String(o.id).slice(-6)}</div>
                  <div className="text-xs">{new Date(o.timestamp).toLocaleString()}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm">Subtotal ${o.subtotal.toFixed(2)}</div>
                  <div className="text-xs">COGS ${o.cogs.toFixed(2)}</div>
                </div>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                {o.items.map((it, idx) => (
                  <div key={idx} className="p-1 rounded border">
                    <div className="font-medium">{it.name}</div>
                    <div className="text-xs">{it.qty} x ${it.price.toFixed(2)} (cost ${it.cost.toFixed(2)})</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  function ExpensesEditor() {
    const [n, setN] = useState("");
    const [a, setA] = useState("");
    return (
      <div className="bg-white p-4 rounded-2xl shadow-md">
        <h3 className="text-lg font-semibold mb-3">Expenses</h3>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!n || !a) return;
            addExpense(n, a);
            setN("");
            setA("");
          }}
          className="flex gap-2"
        >
          <input value={n} onChange={(e) => setN(e.target.value)} placeholder="Expense name" className="p-2 border rounded" />
          <input value={a} onChange={(e) => setA(e.target.value)} placeholder="Amount" type="number" className="p-2 border rounded" />
          <button className="px-3 py-1 rounded-2xl">Add</button>
        </form>
        <div className="mt-3 space-y-2">
          {expenses.map((ex) => (
            <div key={ex.id} className="flex items-center justify-between border p-2 rounded">
              <div>
                <div className="font-medium">{ex.name}</div>
                <div className="text-sm">${Number(ex.amount).toFixed(2)}</div>
              </div>
              <div>
                <button onClick={() => removeExpense(ex.id)} className="px-3 py-1 rounded-2xl border">Delete</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 bg-gradient-to-br from-slate-100 to-white">
      <div className="max-w-6xl mx-auto">
        <header className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-extrabold">Restaurant Profit Manager</h1>
            <p className="text-sm text-slate-600">Track orders, costs, expenses and calculate profit — lightweight & local.</p>
          </div>
          <div className="flex gap-2 items-center">
            <div className="text-sm text-slate-700">Net: <span className="font-semibold">${netProfit.toFixed(2)}</span></div>
            <button onClick={() => { localStorage.clear(); location.reload(); }} className="px-3 py-2 rounded-2xl border">Clear All Storage</button>
          </div>
        </header>

        <main className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="col-span-2 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <MenuEditor />
              <MenuList />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <CartPanel />
              <SummaryPanel />
            </div>

            <div>
              <OrdersList />
            </div>
          </div>

          <aside className="space-y-4">
            <ExpensesEditor />
            <div className="bg-white p-4 rounded-2xl shadow-md">
              <h3 className="text-lg font-semibold mb-3">Quick Actions</h3>
              <div className="flex flex-col gap-2">
                <button onClick={seedSample} className="px-3 py-2 rounded-2xl">Load Sample Menu</button>
                <button onClick={exportOrdersCSV} className="px-3 py-2 rounded-2xl">Export Orders CSV</button>
                <button onClick={resetDay} className="px-3 py-2 rounded-2xl border">Reset Day</button>
              </div>
            </div>

            <div className="p-4 text-sm text-slate-600">Tip: Edit menu items and set cost values — the app uses those to compute COGS and profit. Inventory is optional and will be decremented when orders are placed.</div>
          </aside>
        </main>

        <footer className="mt-8 text-center text-sm text-slate-500">Built for quick daily tracking — export CSV for long-term bookkeeping.</footer>
      </div>
    </div>
  );
}
