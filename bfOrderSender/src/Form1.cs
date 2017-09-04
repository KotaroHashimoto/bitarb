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

namespace bfOrderBook
{
    public partial class Form1 : Form
    {

        BitflyerClient client;
        Board board;
        List<double> amounts;
        List<double> prices;

        double amount;
        double price;

        bool mask = false;
        int SMAX = 0;

        string[] ss = new string[] {
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

        List<RadioButton> choices = null;

        string s19 = new string(' ', 19);
        string s46 = new string(' ', 46);
        string sc = ":";

        public Form1()
        {
            InitializeComponent();
        }


        async Task getPosition()
        {
            Collateral col = null;

            try
            {
                col = await client.GetMyCollateral();
            }
            catch (Exception ex)
            {
                label2.Text = "Failed to get collateral info.";

//                Console.WriteLine(ex);

                return;
            }

            label2.Text = "Equity: " + Math.Round(col.CollateralAmount).ToString() + " JPY (PL: " + (0 < col.OpenPositionProfitAndLoss ? "+" : "") + Math.Round(col.OpenPositionProfitAndLoss).ToString() + " JPY,  Margin: " + Math.Round(col.KeepRate * 100, 1).ToString() + " %)";

            //            label2.Text = "Equity: " + col.CollateralAmount.ToString() + " (PL:" + col.OpenPositionProfitAndLoss.ToString() + ")";
            //            label3.Text = "Keep Rate: " + col.KeepRate.ToString() + " % (Margin:" + col.RequiredCollateral.ToString() + ")";

//            Console.WriteLine("Equity: " + col.CollateralAmount.ToString() + " (PL:" + col.OpenPositionProfitAndLoss.ToString() + ")");
//            Console.WriteLine("Keep Rate: " + col.KeepRate.ToString() + " % (Margin:" + col.RequiredCollateral.ToString() + ")");

            List<Position> pos = null;

            try
            {
                pos = await client.GetMyPositions();
            }
            catch (Exception ex)
            {
                listBox2.BeginUpdate();
                listBox2.Items.Clear();
                listBox2.Items.Add("Failed to get position info.");
                listBox2.EndUpdate();

//                Console.WriteLine(ex);

                return;
            }

            Console.WriteLine("pos.Count = " + pos.Count.ToString());

            listBox2.BeginUpdate();
            listBox2.Items.Clear();

            foreach (Position ps in pos)
            {
                /*
                Console.WriteLine("SwapPointAccumulate = " + ps.SwapPointAccumulate.ToString());
                Console.WriteLine("RequiredCollateral = " + ps.RequiredCollateral.ToString());
                Console.WriteLine("Comission = " + ps.Comission.ToString());
                Console.WriteLine("Price = " + ps.Price.ToString());
                Console.WriteLine("Leverage = " + ps.Leverage.ToString());
                Console.WriteLine("OpenDate = " + ps.OpenDate.ToString());
                Console.WriteLine("ProductCode = " + ps.ProductCode.ToString());
                */

                string side = ps.Side.ToString();

                double pl = ps.ProfitAndLoss + ps.SwapPointAccumulate;
                string[] amount = ps.Size.ToString().Split('.');
                string spl = (0 < pl ? "+" : "") + Math.Round(pl).ToString();

                listBox2.Items.Add(ss[4 - side.Length] + side +
                                   ss[4 - amount[0].Length] + amount[0] +
                                   (amount.Length == 2 ? ("." + amount[1] + ss[8 - amount[1].Length]) : ss[9]) + 
                                   " at " + Math.Round(ps.Price).ToString() +
                                   " (PL: " + spl + " JPY)");   
            }
            
            if(pos.Count == 0)
            {
                listBox2.Items.Add("No Open Position.");
            }

            listBox2.EndUpdate();
        }

        async Task getOrderBook()
        {

            List<string> orderBookA = null;
            List<string> orderBookB = null;
            List<string> orderBook = null;
            amounts = null;
            prices = null;

            bool first = true;

            choices = new List<RadioButton>(18);
            choices.Add(radioButton1);
            choices.Add(radioButton2);
            choices.Add(radioButton3);
            choices.Add(radioButton4);
            choices.Add(radioButton5);
            choices.Add(radioButton6);
            choices.Add(radioButton7);
            choices.Add(radioButton8);
            choices.Add(radioButton9);
            choices.Add(radioButton10);
            choices.Add(radioButton11);
            choices.Add(radioButton12);
            choices.Add(radioButton13);
            choices.Add(radioButton14);
            choices.Add(radioButton15);
            choices.Add(radioButton16);
            choices.Add(radioButton17);
            choices.Add(radioButton18);


            radioButton1.Checked = true;
            listBox1.Items.Add("Connecting to BitFlyer server ...");


            while (true)
            {
                await getPosition();
                label6.Text = "";

                if (!first)
                {
                    if (listBox1.DataSource.Equals(orderBookA))
                    {
                        orderBook = orderBookB;
                    }
                    else
                    {
                        orderBook = orderBookA;
                    }
                    orderBook.Clear();
                    amounts.Clear();
                    prices.Clear();
                }

                try
                {
                    board = await client.GetBoard();
                }
                catch (Exception ex)
                {
                    listBox1.BeginUpdate();
                    listBox1.DataSource = null;
                    listBox1.Items.Add("Connecting to BitFlyer server ...");
                    listBox1.Items.Add(ex);
                    listBox1.EndUpdate();

                    Console.WriteLine(ex);

                    first = true;

                    await Task.Delay(1000);
                    continue;
                }

                if (first)
                {
                    SMAX = Math.Max(board.Asks.Count, board.Bids.Count) + 50;

                    orderBookA = new List<string>(SMAX * 2 + 1);
                    orderBookB = new List<string>(SMAX * 2 + 1);
                    orderBook = orderBookA;

                    amounts = new List<double>(SMAX * 2 + 1);
                    prices = new List<double>(SMAX * 2 + 1);
                }


                int n = SMAX - board.Asks.Count;
                for (int i = 0; i < n; i++)
                {
                    String index = (SMAX - i).ToString();
                    orderBook.Add(ss[4 - index.Length] + index + sc);
                    amounts.Add(0.1);
                    prices.Add(0);
                }

                for (int i = (0 < n ? board.Asks.Count : SMAX) - 1; 0 <= i; i--)
                {
                    String index = (i + 1).ToString();
                    String[] ask = board.Asks[i].Size.ToString().Split('.');
                    String pr = board.Asks[i].Price.ToString();

                    orderBook.Add(ss[4 - index.Length] + index + sc +
                        ss[5 - ask[0].Length] + ask[0] + (ask.Length == 2 ? ("." + ask[1] + ss[8 - ask[1].Length]) : ss[9]) +
                        ss[9 - pr.Length] + pr);

                    amounts.Add(board.Asks[i].Size);
                    prices.Add(board.Asks[i].Price);
                }


                String p = board.MiddlePrice.ToString();
                orderBook.Add(s19 + ss[9 - p.Length] + p + 
                    ss[6] + "spread: " + Math.Round(100 * (board.Asks[0].Price - board.Bids[0].Price) / board.MiddlePrice, 5).ToString() + " %");
                amounts.Add(0);
                prices.Add(board.MiddlePrice);


                n = SMAX - board.Bids.Count;
                for (int i = 0; i < (0 < n ? board.Bids.Count : SMAX); i++)
                {
                    String index = (i + 1).ToString();
                    String[] bid = board.Bids[i].Size.ToString().Split('.');
                    String pr = board.Bids[i].Price.ToString();

                    orderBook.Add(s19 +
                        ss[9 - pr.Length] + pr + ss[2] +
                        ss[5 - bid[0].Length] + bid[0] + (bid.Length == 2 ? ("." + bid[1] + ss[8 - bid[1].Length]) : ss[9]) +
                        ss[2] + sc + ss[4 - index.Length] + index);

                    amounts.Add(-1 * board.Bids[i].Size);
                    prices.Add(board.Bids[i].Price);
                }

                for (int i = 0; i < n; i++)
                {
                    String index = (board.Bids.Count + i + 1).ToString();
                    orderBook.Add(s46 + sc + ss[4 - index.Length] + index);
                    amounts.Add(-0.1);
                    prices.Add(0);
                }


                int foc = listBox1.SelectedIndex;
                int pos = listBox1.TopIndex;

                if (!mask)
                {
                    listBox1.BeginUpdate();
                    listBox1.DataSource = orderBook;
                    listBox1.EndUpdate();
                }

                if (listBox1.DataSource == null)
                {
                    await Task.Delay(1000);
                    continue;
                }

                listBox1.SelectedIndex = foc;
                listBox1.TopIndex = pos;

                if (first)
                {
                    listBox1.TopIndex = SMAX - 20;
                    first = false;
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

            int index = listBox1.SelectedIndex;

            if (index < prices.Count) { 
                textBox3.Text = prices[index].ToString();
            }
        }



        private void listBox1_MouseUp(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void listBox1_MouseDown(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            if(listBox1.DataSource == null)
            {
                return;
            }

            if (Int32.TryParse(textBox1.Text, out int numValue))
            {
                if (board.MiddlePrice == numValue)
                {
                    listBox1.SelectedIndex = SMAX;
                    listBox1.TopIndex = listBox1.SelectedIndex - 20;
                }
                else if (board.MiddlePrice < numValue)
                {
                    for (int i = 0; i < board.Asks.Count; i++)
                    {
                        if (numValue < board.Asks[i].Price)
                        {
                            listBox1.SelectedIndex = SMAX - i;
                            listBox1.TopIndex = listBox1.SelectedIndex - 20;

                            break;
                        }
                    }
                }
                else
                {
                    for (int i = 0; i < board.Bids.Count; i++)
                    {
                        if (board.Bids[i].Price < numValue)
                        {
                            listBox1.SelectedIndex = SMAX + i;
                            listBox1.TopIndex = listBox1.SelectedIndex - 20;

                            break;
                        }
                    }
                }
            }
        }

        private async void Form1_Load(object sender, EventArgs e)
        {

            String key = bfOrderSender.Properties.Settings.Default.key;
            String secret = bfOrderSender.Properties.Settings.Default.secret;

            if (key != null && secret != null && 0 < key.Length && 0 < secret.Length)
            {
                // use stored value
            }
            else if (InputBox(ref key, ref secret) != DialogResult.OK)
            {
                bfOrderSender.Properties.Settings.Default.key = "";
                bfOrderSender.Properties.Settings.Default.secret = "";
                bfOrderSender.Properties.Settings.Default.Save();

                listBox1.Items.Add("Failed to read API key.");
                Application.Exit();
            }

            if (key != null && secret != null && 0 < key.Length && 0 < secret.Length)
            {
                bfOrderSender.Properties.Settings.Default.key = key;
                bfOrderSender.Properties.Settings.Default.secret = secret;
                bfOrderSender.Properties.Settings.Default.Save();

                client = new BitflyerClient(key, secret, ProductCode.FX_BTC_JPY);
                await getOrderBook();
            }
            else
            {
                bfOrderSender.Properties.Settings.Default.key = "";
                bfOrderSender.Properties.Settings.Default.secret = "";
                bfOrderSender.Properties.Settings.Default.Save();

                listBox1.Items.Add("Failed to read API key.");
                Application.Exit();
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (listBox1.DataSource == null)
            {
                return;
            }

            listBox1.SelectedIndex = SMAX;
            listBox1.TopIndex = listBox1.SelectedIndex - 20;
        }

        private void listBox1_DrawItem(object sender, DrawItemEventArgs e)
        {

            e.DrawBackground();

            if (-1 < e.Index)
            {
                if (amounts != null && e.Index < amounts.Count) {

                    Brush b = null;
                    double a = amounts[e.Index];

                    if ((e.State & DrawItemState.Selected) != DrawItemState.Selected)
                    {
                        e.Graphics.FillRectangle(new SolidBrush(button2.ForeColor), e.Bounds);

                        if (100.0 <= a)
                        {
                            b = new SolidBrush(button6.ForeColor);
                        }
                        else if (10.0 <= a)
                        {
                            b = new SolidBrush(button5.ForeColor);
                        }
                        else if (1.0 <= a)
                        {
                            b = new SolidBrush(button4.ForeColor);
                        }
                        else if (0 <= a)
                        {
                            b = new SolidBrush(button3.ForeColor);
                        }

                        else if (a <= -100.0)
                        {
                            b = new SolidBrush(button10.ForeColor);
                        }
                        else if (a <= -10.0)
                        {
                            b = new SolidBrush(button9.ForeColor);
                        }
                        else if (a <= -1.0)
                        {
                            b = new SolidBrush(button8.ForeColor);
                        }
                        else
                        {
                            b = new SolidBrush(button7.ForeColor);
                        }
                    }
                    else
                    {
                        b = new SolidBrush(e.ForeColor);
                    }

                    e.Graphics.DrawString(((ListBox)sender).Items[e.Index].ToString(), e.Font, b, e.Bounds);
                    b.Dispose();
                }
                else
                {
                    e.Graphics.DrawString(((ListBox)sender).Items[e.Index].ToString(), e.Font, new SolidBrush(button3.ForeColor), e.Bounds);
                }
            }

            e.DrawFocusRectangle();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button2.ForeColor;

            if(cd.ShowDialog() == DialogResult.OK)
            {
                button2.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.back = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button3.ForeColor;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                button3.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.a = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button4_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button4.ForeColor;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                button4.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.a_1 = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button5_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button5.ForeColor;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                button5.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.a_10 = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button6_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button6.ForeColor;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                button6.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.a_100 = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button7_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button7.ForeColor;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                button7.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.b = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button8_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button8.ForeColor;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                button8.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.b_1 = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button9_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button9.ForeColor;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                button9.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.b_10 = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button10_Click(object sender, EventArgs e)
        {
            ColorDialog cd = new ColorDialog();
            cd.AllowFullOpen = true;
            cd.Color = button10.ForeColor;

            if (cd.ShowDialog() == DialogResult.OK)
            {
                button10.ForeColor = cd.Color;
            }

            bfOrderSender.Properties.Settings.Default.b_100 = cd.Color;
            bfOrderSender.Properties.Settings.Default.Save();
        }

        private void button11_Click(object sender, EventArgs e)
        {
            bfOrderSender.Properties.Settings.Default.key = "";
            bfOrderSender.Properties.Settings.Default.secret = "";
            bfOrderSender.Properties.Settings.Default.Save();

            Application.Exit();
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


        private void textBox2_TextChanged(object sender, EventArgs e)
        {
            if (Double.TryParse(textBox2.Text, out amount))
            {
                if (amount <= 0)
                {
                    sellMarket.Enabled = false;
                    buyMarket.Enabled = false;

                    textBox3_TextChanged(sender, e);

                    return;
                }

                string[] am = textBox2.Text.Split('.');
                if (1 < am.Length)
                {
                    if (am[1].Length < 4)
                    {
                        sellMarket.Enabled = true;
                        buyMarket.Enabled = true;

                        textBox3_TextChanged(sender, e);

                        return;
                    }
                }
                else
                {
                    sellMarket.Enabled = true;
                    buyMarket.Enabled = true;

                    textBox3_TextChanged(sender, e);

                    return;
                }
            }

            sellMarket.Enabled = false;
            buyMarket.Enabled = false;

            textBox3_TextChanged(sender, e);
        }


        private void textBox3_TextChanged(object sender, EventArgs e)
        {
            if (Double.TryParse(textBox3.Text, out price))
            {
                if (price <= 0)
                {
                    sellLimit.Enabled = false;
                    buyLimit.Enabled = false;

                    return;
                }

                if (textBox3.Text.Split('.').Length == 1)
                {
                    if (sellMarket.Enabled && buyMarket.Enabled) { 
                        sellLimit.Enabled = true;
                        buyLimit.Enabled = true;

                        return;
                    }
                }
            }

            sellLimit.Enabled = false;
            buyLimit.Enabled = false;
        }


        private async void sellMarket_Click(object sender, EventArgs e)
        {
            try
            {
                label6.Text = "Sell Market " + amount.ToString() + " BTC Requesting";
                await client.Sell(amount);
                label6.Text = "Sell Market " + amount.ToString() + " BTC Accepted";
            }
            catch (Exception ex)
            {
                label6.Text = "Sell Market " + amount.ToString() + " BTC Failed.";
                label6.Text += "\n" + ex.ToString();

                Console.WriteLine(ex);
                await Task.Delay(5000);
            }

            await Task.Delay(3000);
        }

        private async void buyMarket_Click(object sender, EventArgs e)
        {
            try
            {
                label6.Text = "Buy Market " + amount.ToString() + " BTC Requesting";
                await client.Buy(amount);
                label6.Text = "Buy Market " + amount.ToString() + " BTC Accepted";
            }
            catch (Exception ex)
            {
                label6.Text = "Buy Market " + amount.ToString() + " BTC Failed.";
                label6.Text += "\n" + ex.ToString();

                Console.WriteLine(ex);
                await Task.Delay(5000);
            }

            await Task.Delay(3000);
        }

        private async void sellLimit_Click(object sender, EventArgs e)
        {
            try
            {
                label6.Text = "Sell Limit " + amount.ToString() + " BTC Requesting";
                await client.Sell(price, amount);
                label6.Text = "Sell Limit " + amount.ToString() + " BTC Accepted";
            }
            catch (Exception ex)
            {
                label6.Text = "Sell Limit " + amount.ToString() + " BTC Failed.";
                label6.Text += "\n" + ex.ToString();

                Console.WriteLine(ex);
                await Task.Delay(5000);
            }

            await Task.Delay(3000);
        }

        private async void buyLimit_Click(object sender, EventArgs e)
        {
            try
            {
                label6.Text = "Buy Limit " + amount.ToString() + " BTC Requesting";
                await client.Buy(price, amount);
                label6.Text = "Buy Limit " + amount.ToString() + " BTC Accepted";
            }
            catch (Exception ex)
            {
                label6.Text = "Buy Limit " + amount.ToString() + " BTC Failed.";
                label6.Text += "\n" + ex.ToString();

                Console.WriteLine(ex);
                await Task.Delay(5000);
            }

            await Task.Delay(3000);
        }


        private double getDelta()
        {
            foreach (RadioButton r in choices)
            {
                if(r.Checked)
                {
                    if (Double.TryParse(r.Text, out double delta))
                    {
                        return delta;
                    }
                    else {
                        break;
                    }
                }
            }

            return 0;
        }


        private void amountInc_Click(object sender, EventArgs e)
        {
            if (Double.TryParse(textBox2.Text, out amount))
            {
                double delta = getDelta();
                if (0 < amount + delta)
                {
                    textBox2.Text = (amount + delta).ToString();
                }
            }
        }

        private void amountDec_Click(object sender, EventArgs e)
        {
            if (Double.TryParse(textBox2.Text, out amount))
            {
                double delta = getDelta();
                if (0 < amount - delta)
                {
                    textBox2.Text = (amount - delta).ToString();
                }
            }
        }

        private void priceInc_Click(object sender, EventArgs e)
        {
            if (Double.TryParse(textBox3.Text, out price))
            {
                double delta = getDelta();
                if (0 < price + delta && 1 <= delta)
                {
                    textBox3.Text = (price + delta).ToString();
                }
            }
        }

        private void priceDec_Click(object sender, EventArgs e)
        {
            if (Double.TryParse(textBox3.Text, out price))
            {
                double delta = getDelta();
                if (0 < price - delta && 1 <= delta)
                {
                    textBox3.Text = (price - delta).ToString();
                }
            }
        }

        private void radioButton18_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton17_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton14_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton13_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton12_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton11_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton1_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton2_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton3_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton4_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton5_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton6_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton7_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton8_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton9_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton10_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton15_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void radioButton16_CheckedChanged(object sender, EventArgs e)
        {
            amountInc_Click(sender, e);
        }

        private void listBox2_DrawItem(object sender, DrawItemEventArgs e)
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
