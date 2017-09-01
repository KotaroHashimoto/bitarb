using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

using BitflyerApi;
using System.Net;

namespace bfCanceller
{

    public partial class Form1 : Form
    {

        String[] ss = new string[] {
                    "",
                    " ",
                    "  ",
                    "   ",
                    "    ",
                    "     ",
                    "      ",
                    "       ",
                    "        ",
                    "         "};

        bool mask = false;
        bool processing = false;
        BitflyerClient client = null;

        List<Order> orders = null;

        public Form1()
        {
            InitializeComponent();

            client = new BitflyerClient("", "", ProductCode.FX_BTC_JPY);
        }

        async Task getOpenOrders()
        {

            List<string> orderListA = new List<string>();
            List<string> orderListB = new List<string>();
            List<string> orderList = orderListA;

            listBox1.Items.Add("Connecting to BitFlyer server ...");


            while (true)
            {
                if (listBox1.DataSource != null)
                {
                    if (listBox1.DataSource.Equals(orderListA))
                    {
                        orderList = orderListB;
                    }
                    else
                    {
                        orderList = orderListA;
                    }
                }

                if(orderList != null)
                {
                    orderList.Clear();
                }

                try
                {
                    orders = await client.GetMyActiveOrders();
                }
                catch (Exception ex)
                {
                    listBox1.DataSource = null;
                    listBox1.Items.Add(ex);
                    listBox1.Items.Add("Connecting to BitFlyer server ...");

                    Properties.Settings.Default.key = "";
                    Properties.Settings.Default.secret = "";
                    Properties.Settings.Default.Save();

                    await Task.Delay(1000);
                    continue;
                }

                if (orders == null)
                {
                    orderList.Add("No Open Order.");
                }
                else if(orders.Count == 0)
                {
                    orderList.Add("No Open Order.");
                }
                else
                {
                    foreach (Order oo in orders)
                    {
                        string side = oo.Side.ToString();
                        string[] amount = oo.OutstandingSize.ToString().Split('.');
                        string price = oo.Price.ToString();
                        string date = oo.Date.ToLongTimeString() + ss[1] + oo.Date.ToShortDateString();

                        orderList.Add(ss[5 - side.Length] + side + ss[5 - amount[0].Length] + amount[0] +
                            (amount.Length == 2 ? ("." + amount[1] + ss[8 - amount[1].Length]) : ss[9]) + " BTC at " +
                            ss[7 - price.Length] + price + ss[3] + date);
                    }
                }

                int foc = listBox1.SelectedIndex;
                int pos = listBox1.TopIndex;

                if (!mask)
                {
                    listBox1.BeginUpdate();
                    listBox1.DataSource = orderList;
                    listBox1.EndUpdate();
                }

                if (orders == null)
                {
                    // do nothing
                }
                else 
                {
                    listBox1.SelectedIndex = (foc < orders.Count) ? foc : 0;
                    listBox1.TopIndex = (pos < orders.Count) ? pos : 0;
                }


                await Task.Delay(1000);
            }
        }


        private void listBox1_MouseCaptureChanged(object sender, EventArgs e)
        {
            mask = !mask;
        }

        private void listBox1_MouseClick(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void listBox1_MouseUp(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void listBox1_MouseDown(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private async void listBox1_MouseDoubleClick(object sender, MouseEventArgs e)
        {

            if (!processing && orders != null)
            {
                processing = true;

                try
                {
                    if (listBox1.SelectedIndex < orders.Count) {
                        await client.CancelOrder(orders.ElementAt(listBox1.SelectedIndex));
                    }
                }
                catch (Exception ex)
                {
                    listBox1.DataSource = null;
                    listBox1.Items.Add(ex);
                    listBox1.Items.Add("Failed to cancel order.");

                    Properties.Settings.Default.key = "";
                    Properties.Settings.Default.secret = "";
                    Properties.Settings.Default.Save();

                    await Task.Delay(1000);
                }

                processing = false;
            }
        }

        private async void Form1_Load(object sender, EventArgs e)
        {

            String key = Properties.Settings.Default.key;
            String secret = Properties.Settings.Default.secret;

            if (key != null && secret != null && 0 < key.Length && 0 < secret.Length)
            {
                // use stored value
            }
            else if (InputBox(ref key, ref secret) != DialogResult.OK)
            {
                Properties.Settings.Default.key = "";
                Properties.Settings.Default.secret = "";
                Properties.Settings.Default.Save();

                listBox1.Items.Add("Failed to read API key.");
            }

            if (key != null && secret != null && 0 < key.Length && 0 < secret.Length)
            {
                Properties.Settings.Default.key = key;
                Properties.Settings.Default.secret = secret;
                Properties.Settings.Default.Save();

                client = new BitflyerClient(key, secret, ProductCode.FX_BTC_JPY);
                await getOpenOrders();
            }
            else
            {
                Properties.Settings.Default.key = "";
                Properties.Settings.Default.secret = "";
                Properties.Settings.Default.Save();

                listBox1.Items.Add("Failed to read API key.");
            }
        }

        private async void button1_Click(object sender, EventArgs e)
        {
            try
            {
                await client.CancelAllOrders();
            }
            catch (Exception ex)
            {
                listBox1.DataSource = null;
                listBox1.Items.Add(ex);
                listBox1.Items.Add("Failed to cancel all orders.");

                Properties.Settings.Default.key = "";
                Properties.Settings.Default.secret = "";
                Properties.Settings.Default.Save();

                await Task.Delay(1000);
            }
        }


        public static DialogResult InputBox(ref string key, ref string secret)
        {
            Form form = new Form();
            Label label0 = new Label();
            TextBox textBox0 = new TextBox();
            Label label1 = new Label();
            TextBox textBox1 = new TextBox();
            Button buttonOk = new Button();
            Button buttonCancel = new Button();

            form.Text = "Input your BitFlyer Lightning Credential.";
            label0.Text = "API Key";
            textBox0.Text = key;
            label1.Text = "API Secret";
            textBox1.Text = secret;

            buttonOk.Text = "OK";
            buttonCancel.Text = "Cancel";
            buttonOk.DialogResult = DialogResult.OK;
            buttonCancel.DialogResult = DialogResult.Cancel;

            label0.SetBounds(9, 20, 372, 13);
            textBox0.SetBounds(12, 36, 372, 20);
            label1.SetBounds(9, 20 + 55, 372, 13);
            textBox1.SetBounds(12, 36 + 55, 372, 20);
            buttonOk.SetBounds(228, 72 + 55, 75, 23);
            buttonCancel.SetBounds(309, 72 + 55, 75, 23);

            label0.AutoSize = true;
            textBox0.Anchor = textBox0.Anchor | AnchorStyles.Right;
            label1.AutoSize = true;
            textBox1.Anchor = textBox1.Anchor | AnchorStyles.Right;
            buttonOk.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            buttonCancel.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;

            form.ClientSize = new Size(396, 107 + 55);
            form.Controls.AddRange(new Control[] { label0, textBox0, label1, textBox1, buttonOk, buttonCancel });
            form.ClientSize = new Size(Math.Max(300, label0.Right + 10), form.ClientSize.Height);
            form.FormBorderStyle = FormBorderStyle.FixedDialog;
            form.StartPosition = FormStartPosition.CenterScreen;
            form.MinimizeBox = false;
            form.MaximizeBox = false;
            form.AcceptButton = buttonOk;
            form.CancelButton = buttonCancel;

            DialogResult dialogResult = form.ShowDialog();
            key = textBox0.Text;
            secret = textBox1.Text;

            return dialogResult;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            Properties.Settings.Default.key = "";
            Properties.Settings.Default.secret = "";
            Properties.Settings.Default.Save();

            Application.Exit();
        }

        private void listBox1_DrawItem(object sender, DrawItemEventArgs e)
        {

            e.DrawBackground();

            if (-1 < e.Index && e.Index < listBox1.Items.Count)
            {
                Brush b = null;
                string txt = ((ListBox)sender).Items[e.Index].ToString();

                if ((e.State & DrawItemState.Selected) != DrawItemState.Selected)
                {
                    if (txt.Contains("SELL"))
                    {
                        b = new SolidBrush(Color.Blue);
                    }
                    else if (txt.Contains("BUY"))
                    {
                        b = new SolidBrush(Color.Red);
                    }
                    else
                    {
                        b = new SolidBrush(e.ForeColor);
                    }
                }
                else
                {
                    b = new SolidBrush(e.ForeColor);
                }

                e.Graphics.DrawString(txt, e.Font, b, e.Bounds);
                b.Dispose();
            }

            e.DrawFocusRectangle();
        }
    }
}
